use serde::{Deserialize, Serialize};
use std::collections::VecDeque;
use std::io::{self, Read};

const MAX_HEIGHT: usize = 512;
const MAX_WIDTH: usize = 512;

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

fn write_response(resp: &MazeResp) {
    let payload = serde_json::to_string(resp).unwrap_or_else(|_| {
        "{\"length\":null,\"error\":\"internal serialization error\"}".to_string()
    });
    println!("{}", payload);
}

fn main() {
    let mut input = String::new();
    if io::stdin().read_to_string(&mut input).is_err() {
        write_response(&MazeResp {
            length: None,
            error: Some("failed to read request".to_string()),
        });
        return;
    }

    let req: MazeReq = match serde_json::from_str(&input) {
        Ok(v) => v,
        Err(err) => {
            write_response(&MazeResp {
                length: None,
                error: Some(format!("invalid json: {}", err)),
            });
            return;
        }
    };

    if let Err(err) = validate(&req) {
        write_response(&MazeResp {
            length: None,
            error: Some(err),
        });
        return;
    }

    write_response(&MazeResp {
        length: bfs(&req.grid, req.start, req.goal),
        error: None,
    });
}

#[cfg(test)]
mod tests {
    use super::{bfs, validate, MazeReq};

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
}
