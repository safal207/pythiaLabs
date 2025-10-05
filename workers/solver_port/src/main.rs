use serde::{Deserialize, Serialize};
use std::io::{self, Read};
use std::collections::VecDeque;

#[derive(Deserialize)]
struct MazeReq {
    grid: Vec<Vec<u8>>, // 0=free, 1=wall
    start: (usize, usize),
    goal: (usize, usize),
}

#[derive(Serialize)]
struct MazeResp { length: Option<usize> }

fn bfs(grid: &Vec<Vec<u8>>, start: (usize, usize), goal: (usize, usize)) -> Option<usize> {
    let (h, w) = (grid.len(), grid[0].len());
    let mut dist = vec![vec![usize::MAX; w]; h];
    let mut q = VecDeque::new();
    dist[start.0][start.1] = 0;
    q.push_back(start);
    let dirs = [(1,0),(-1,0),(0,1),(0,-1)];
    while let Some((r,c)) = q.pop_front() {
        if (r,c) == goal { return Some(dist[r][c]); }
        for (dr,dc) in dirs.iter() {
            let (nr, nc) = (r as isize + dr, c as isize + dc);
            if nr>=0 && nc>=0 {
                let (nr, nc) = (nr as usize, nc as usize);
                if nr<h && nc<w && grid[nr][nc]==0 && dist[nr][nc]==usize::MAX {
                    dist[nr][nc] = dist[r][c] + 1;
                    q.push_back((nr,nc));
                }
            }
        }
    }
    None
}

fn main() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap();
    let req: MazeReq = serde_json::from_str(&input).unwrap();
    let ans = bfs(&req.grid, req.start, req.goal);
    let out = MazeResp { length: ans };
    println!("{}", serde_json::to_string(&out).unwrap());
}
