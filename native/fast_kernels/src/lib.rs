use rustler::Encoder;

#[rustler::nif]
fn levenshtein(a: String, b: String) -> usize {
    let xs: Vec<char> = a.chars().collect();
    let ys: Vec<char> = b.chars().collect();
    let (m, n) = (xs.len(), ys.len());
    let mut prev: Vec<usize> = (0..=n).collect();
    let mut curr: Vec<usize> = vec![0; n + 1];
    for i in 1..=m {
        curr[0] = i;
        for j in 1..=n {
            let cost = if xs[i - 1] == ys[j - 1] { 0 } else { 1 };
            let insert = curr[j - 1] + 1;
            let delete = prev[j] + 1;
            let replace = prev[j - 1] + cost;
            curr[j] = insert.min(delete).min(replace);
        }
        std::mem::swap(&mut prev, &mut curr);
    }
    prev[n]
}

rustler::init!("Elixir.Pythia.Kernels", [levenshtein]);
