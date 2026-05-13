import socket
import struct
import statistics
import numpy as np
import pandas as pd

HOST = "154.57.164.74"  # The server's hostname or IP address
PORT = 32077  # The port used by the server

def recv_bytes(conn, n_bytes):
    sample_buffer = b''
    while len(sample_buffer) < n_bytes:
        remaining = n_bytes - len(sample_buffer)
        sample_buffer += conn.recv(remaining)
    return sample_buffer

def socket_readline(conn):
    buffer = b''
    while True:
        r_chr = recv_bytes(conn, 1)
        buffer += r_chr
        if r_chr == b'\n':
            break
    return buffer


def recv_trace(conn):
    label_prefix = recv_bytes(conn, 4)
    label_len = struct.unpack("<L", label_prefix)[0]
    label = recv_bytes(conn, label_len).decode()

    trace_prefix = recv_bytes(conn, 4)
    trace_len = struct.unpack("<L", trace_prefix)[0]

    sample_size = 4 # 4 bytes per float
    sample_buffer = recv_bytes(conn, trace_len * sample_size)

    trace = []
    for i in range(trace_len):
        pos = i*4
        sample = struct.unpack("<f", sample_buffer[pos:pos+sample_size])[0]
        trace.append(sample)

    return (label, trace)

def printtrace(traces):
    print(f"{'NAME':<20}{'MEAN':<12}{'MEDIAN':<12}{'MAX':<12}{'MIN':<12}{'VAR':<15}{'STD DEV':<12}")

    for label in ["trace_led_auth", "trace_led_unlocked", "trace_mcu"]:
        data = traces[label]

        mean = np.mean(data)
        median = np.median(data)
        max_val = np.max(data)
        min_val = np.min(data)
        variance = np.var(data)
        std_dev = np.std(data)
        length = len(data)

        print(f"{label:<20}"
              f"{mean:<12.3f}"
              f"{median:<12.3f}"
              f"{max_val:<12.3f}"
              f"{min_val:<12.3f}"
              f"{variance:<15.3f}"
              f"{std_dev:<12.3f}"
              f"{length:<12.3f}")
        # Plot with Pandas



def send_password(password):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as conn:
        conn.connect((HOST, PORT))

        # consume text
        banner = socket_readline(conn)
        #print(banner.decode())

        # consume text
        req = socket_readline(conn)
        #print(req.decode())

        # There was a print() around this, I removed it
        conn.recv(1024).strip()
        
        conn.send(b'password')
        
        conn.recv(1024).strip()

        #conn.send(b'00000\n')
        conn.send(f"{password}\n".encode())


        traces = {}

        label, trace = recv_trace(conn)
        traces[label] = trace

        label, trace = recv_trace(conn)
        traces[label] = trace

        label, trace = recv_trace(conn)
        traces[label] = trace

        print(traces.keys())
        #print(traces["trace_led_auth"])
        #print(traces["trace_led_unlocked"])
        #print(traces["trace_mcu"])
        printtrace(traces)

send_password("000")
