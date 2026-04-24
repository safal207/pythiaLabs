use serde::{Deserialize, Serialize};
use std::collections::VecDeque;
use std::io::{self, Read, Write};

const MAX_HEIGHT: usize = 512;
const MAX_WIDTH: usize = 512;
const MAX_FRAME_BYTES: usize = 8 * 1024 * 1024;

#[derive(Deserialize)]
struct MazeReq {
    grid: Vec<Vec<u8>>, // 0=free, 1=wall
    start: (usize, usize),
    goal: (usize, usize),
}

#[derive(Serialize)]
struct MazeResp {
    length: Option<usize>,
    error: Option<String>,
}

fn bfs(grid: &[Vec<u8>], start: (usize, usize), goal: (usize, usize)) -> Option<usize> {
    let (h, w) = (grid.len(), grid[0].len());
    let mut dist = vec![vec![usize::MAX; w]; h];
    let mut q = VecDeque::new();
    dist[start.0][start.1] = 0;
    q.push_back(start);
    let dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)];
    while let Some((r, c)) = q.pop_front() {
        if (r, c) == goal {
            return Some(dist[r][c]);
        }
        for (dr, dc) in dirs.iter() {
            let (nr, nc) = (r as isize + dr, c as isize + dc);
            if nr >= 0 && nc >= 0 {
                let (nr, nc) = (nr as usize, nc as usize);
                if nr < h && nc < w && grid[nr][nc] == 0 && dist[nr][nc] == usize::MAX {
                    dist[nr][nc] = dist[r][c] + 1;
                    q.push_back((nr, nc));
                }
            }
        }
    }
    None
}

fn validate(req: &MazeReq) -> Result<(), String> {
    if req.grid.is_empty() {
        return Err("grid must be non-empty".to_string());
    }
    if req.grid.len() > MAX_HEIGHT {
        return Err(format!("grid height exceeds {}", MAX_HEIGHT));
    }

    let width = req.grid[0].len();
    if width == 0 {
        return Err("grid rows must be non-empty".to_string());
    }
    if width > MAX_WIDTH {
        return Err(format!("grid width exceeds {}", MAX_WIDTH));
    }

    for row in &req.grid {
        if row.len() != width {
            return Err("grid must be rectangular".to_string());
        }
        if row.iter().any(|cell| *cell > 1) {
            return Err("grid values must be 0 or 1".to_string());
        }
    }

    let (h, w) = (req.grid.len(), width);
    let in_bounds = |(r, c): (usize, usize)| r < h && c < w;
    if !in_bounds(req.start) {
        return Err("start is out of bounds".to_string());
    }
    if !in_bounds(req.goal) {
        return Err("goal is out of bounds".to_string());
    }
    if req.grid[req.start.0][req.start.1] != 0 {
        return Err("start must be on a free cell".to_string());
    }
    if req.grid[req.goal.0][req.goal.1] != 0 {
        return Err("goal must be on a free cell".to_string());
    }

    Ok(())
}

/// Read a single packet:4 frame (big-endian u32 length prefix + payload).
/// Returns Ok(None) on clean EOF before any bytes are read.
fn read_frame<R: Read>(r: &mut R) -> io::Result<Option<Vec<u8>>> {
    let mut len_buf = [0u8; 4];
    match r.read(&mut len_buf[..1])? {
        0 => return Ok(None),
        _ => {}
    }
    r.read_exact(&mut len_buf[1..])?;
    let len = u32::from_be_bytes(len_buf) as usize;
    if len > MAX_FRAME_BYTES {
        return Err(io::Error::new(
            io::ErrorKind::InvalidData,
            format!("frame length {} exceeds limit", len),
        ));
    }
    let mut payload = vec![0u8; len];
    r.read_exact(&mut payload)?;
    Ok(Some(payload))
}

fn write_frame<W: Write>(w: &mut W, payload: &[u8]) -> io::Result<()> {
    let len = payload.len();
    if len > MAX_FRAME_BYTES {
        return Err(io::Error::new(
            io::ErrorKind::InvalidData,
            "response exceeds frame limit",
        ));
    }
    let len_prefix = (len as u32).to_be_bytes();
    w.write_all(&len_prefix)?;
    w.write_all(payload)?;
    w.flush()
}

fn serialize_response(resp: &MazeResp) -> Vec<u8> {
    serde_json::to_vec(resp).unwrap_or_else(|_| {
        b"{\"length\":null,\"error\":\"internal serialization error\"}".to_vec()
    })
}

fn handle_frame(payload: &[u8]) -> MazeResp {
    let req: MazeReq = match serde_json::from_slice(payload) {
        Ok(v) => v,
        Err(err) => {
            return MazeResp {
                length: None,
                error: Some(format!("invalid json: {}", err)),
            };
        }
    };

    if let Err(err) = validate(&req) {
        return MazeResp {
            length: None,
            error: Some(err),
        };
    }

    MazeResp {
        length: bfs(&req.grid, req.start, req.goal),
        error: None,
    }
}

fn main() {
    let stdin = io::stdin();
    let stdout = io::stdout();
    let mut reader = stdin.lock();
    let mut writer = stdout.lock();

    loop {
        match read_frame(&mut reader) {
            Ok(None) => return,
            Ok(Some(payload)) => {
                let resp = handle_frame(&payload);
                let bytes = serialize_response(&resp);
                if write_frame(&mut writer, &bytes).is_err() {
                    return;
                }
            }
            Err(err) => {
                let resp = MazeResp {
                    length: None,
                    error: Some(format!("protocol error: {}", err)),
                };
                let bytes = serialize_response(&resp);
                let _ = write_frame(&mut writer, &bytes);
                return;
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::{bfs, handle_frame, read_frame, validate, write_frame, MazeReq};
    use std::io::Cursor;

    #[test]
    fn validate_rejects_empty_grid() {
        let req = MazeReq {
            grid: vec![],
            start: (0, 0),
            goal: (0, 0),
        };
        assert!(validate(&req).is_err());
    }

    #[test]
    fn validate_rejects_non_rectangular_grid() {
        let req = MazeReq {
            grid: vec![vec![0, 0], vec![0]],
            start: (0, 0),
            goal: (1, 0),
        };
        assert!(validate(&req).is_err());
    }

    #[test]
    fn bfs_finds_shortest_path() {
        let grid = vec![vec![0, 0, 0], vec![1, 1, 0], vec![0, 0, 0]];
        assert_eq!(bfs(&grid, (0, 0), (2, 2)), Some(4));
    }

    #[test]
    fn frame_roundtrip_preserves_payload() {
        let mut buf: Vec<u8> = Vec::new();
        write_frame(&mut buf, b"{\"ok\":true}").unwrap();
        let mut cursor = Cursor::new(buf);
        let out = read_frame(&mut cursor).unwrap().unwrap();
        assert_eq!(out, b"{\"ok\":true}");
        assert!(read_frame(&mut cursor).unwrap().is_none());
    }

    #[test]
    fn handle_frame_returns_length_for_valid_request() {
        let req = br#"{"grid":[[0,0,0],[1,1,0],[0,0,0]],"start":[0,0],"goal":[2,2]}"#;
        let resp = handle_frame(req);
        assert_eq!(resp.length, Some(4));
        assert!(resp.error.is_none());
    }

    #[test]
    fn handle_frame_reports_validation_errors() {
        let req = br#"{"grid":[[0,0],[0]],"start":[0,0],"goal":[1,0]}"#;
        let resp = handle_frame(req);
        assert!(resp.length.is_none());
        assert!(resp.error.is_some());
    }
}
