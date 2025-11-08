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
    // Validate grid is not empty
    if grid.is_empty() {
        eprintln!("Error: Grid is empty");
        return None;
    }

    let h = grid.len();
    let w = grid[0].len();

    if w == 0 {
        eprintln!("Error: Grid has zero width");
        return None;
    }

    // Validate start and goal positions are within bounds
    if start.0 >= h || start.1 >= w {
        eprintln!("Error: Start position ({}, {}) is out of bounds ({}x{})", start.0, start.1, h, w);
        return None;
    }

    if goal.0 >= h || goal.1 >= w {
        eprintln!("Error: Goal position ({}, {}) is out of bounds ({}x{})", goal.0, goal.1, h, w);
        return None;
    }

    // Check if start or goal are walls
    if grid[start.0][start.1] != 0 {
        eprintln!("Error: Start position is a wall");
        return None;
    }

    if grid[goal.0][goal.1] != 0 {
        eprintln!("Error: Goal position is a wall");
        return None;
    }

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
    // Read input from stdin
    let mut input = String::new();
    if let Err(e) = io::stdin().read_to_string(&mut input) {
        eprintln!("Error reading stdin: {}", e);
        let out = MazeResp { length: None };
        if let Ok(json) = serde_json::to_string(&out) {
            println!("{}", json);
        }
        std::process::exit(1);
    }

    // Parse JSON request
    let req: MazeReq = match serde_json::from_str(&input) {
        Ok(r) => r,
        Err(e) => {
            eprintln!("Error parsing JSON: {}", e);
            let out = MazeResp { length: None };
            if let Ok(json) = serde_json::to_string(&out) {
                println!("{}", json);
            }
            std::process::exit(1);
        }
    };

    // Run BFS
    let ans = bfs(&req.grid, req.start, req.goal);
    let out = MazeResp { length: ans };

    // Serialize and output response
    match serde_json::to_string(&out) {
        Ok(json) => println!("{}", json),
        Err(e) => {
            eprintln!("Error serializing response: {}", e);
            std::process::exit(1);
        }
    }
}
