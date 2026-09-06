use std::collections::HashMap;
use std::env;
use std::fs;

fn load(path: &str) -> HashMap<String, String> {
    let text = fs::read_to_string(path).expect("read vector");
    text.lines()
        .filter(|line| !line.is_empty())
        .map(|line| {
            let (key, value) = line.split_once('=').expect("key=value");
            (key.to_string(), value.to_string())
        })
        .collect()
}

fn main() {
    let path = env::args().nth(1).expect("usage: rust VECTOR");
    let values = load(&path);
    let (verdict, operator, state) =
        if values["verification_label"] == "PRESENT" && values["evidence"] != "PRESENT" {
            ("BACKTRACE", "GLT-0036", "CONTESTED")
        } else if values["source"] == "UNKNOWN" {
            ("BACKTRACE", "GLT-0036", "CONTESTED")
        } else {
            ("ACCEPT", "NONE", "ACCEPTED")
        };

    println!(
        "{}|{}|{}|{}|{}",
        values["vector_id"], values["protocol_version"], verdict, operator, state
    );
}
