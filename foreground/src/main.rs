// src/main.rs
use std::sync::mpsc;
use std::thread;

mod pythonspawn;
use pythonspawn::runpythonfile_stream;

fn main() {
    let (tx, rx) = mpsc::channel::<(&'static str, String)>();

    // Spawn model.py thread
    let tx_model = tx.clone();
    let handle_model = thread::spawn(move || {
        runpythonfile_stream("utils/model.py", "model.py", tx_model);
    });

    // Spawn logging.py thread
    let tx_logging = tx.clone();
    let handle_logging = thread::spawn(move || {
        runpythonfile_stream("utils/logging.py", "logging.py", tx_logging);
    });

    // Drop the original sender in main so rx will close when both worker threads finish
    drop(tx);

    // Receive and print streamed output as it arrives
    while let Ok((tag, line)) = rx.recv() {
        println!("[{tag}] {line}");
    }

    // Wait for threads to finish
    handle_model.join().expect("Model thread panicked");
    handle_logging.join().expect("Logging thread panicked");
}
