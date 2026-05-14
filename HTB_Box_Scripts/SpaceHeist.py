import socket
import struct
import statistics
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import hashlib
import string
from scipy.signal import find_peaks
from collections import Counter

HOST = "154.57.164.67"  # The server's hostname or IP address
PORT = 31136  # The port used by the server
SECRET = b'qvb4a1b07E870B' # secret used for challenge/response
PASSWORD = b'9679216205204468'

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

# def printtrace(traces):
#     print(f"{'NAME':<20}{'MEAN':<12}{'MEDIAN':<12}{'MAX':<12}{'MIN':<12}{'VAR':<15}{'STD DEV':<12}")

#     for label in ["trace_led_auth", "trace_led_unlocked", "trace_mcu"]:
#         data = traces[label]

#         mean = np.mean(data)
#         median = np.median(data)
#         max_val = np.max(data)
#         min_val = np.min(data)
#         variance = np.var(data)
#         std_dev = np.std(data)
#         length = len(data)

#         print(f"{label:<20}"
#               f"{mean:<12.3f}"
#               f"{median:<12.3f}"
#               f"{max_val:<12.3f}"
#               f"{min_val:<12.3f}"
#               f"{variance:<15.3f}"
#               f"{std_dev:<12.3f}"
#               f"{length:<12.3f}")
#         # Plot with Pandas
#         df = pd.DataFrame(
#             {
#                 "data": data
#             },
#             index=[i for i in range(0, len(data))],
#         )
#         df.plot.line()
#         plt.title(label)
#         plt.show()

def printtrace(traces, password):
    fig, axes = plt.subplots(2, 3, figsize=(20, 8))
    fig.suptitle("Trace Analysis {}".format(password), fontsize=14, fontweight="bold")
    labels = ["trace_led_auth", "trace_led_unlocked", "trace_mcu"]
    positions = [(0, 0), (0, 1), (1, 0)]  # top-left, top-middle, bottom-left
    stats_lines = [
        f"{'NAME':<20}{'MEAN':<10}{'MEDIAN':<10}{'MAX':<10}{'MIN':<10}{'VAR':<12}{'STD':<10}{'N':<6}"
    ]

    spike_widths = []
    last_spike_data = []

    for label, (row, col) in zip(labels, positions):
        data = traces[label]
        mean     = np.mean(data)
        median   = np.median(data)
        max_val  = np.max(data)
        min_val  = np.min(data)
        variance = np.var(data)
        std_dev  = np.std(data)
        length   = len(data)
        stats_lines.append(
            f"{label:<20}{mean:<10.3f}{median:<10.3f}{max_val:<10.3f}"
            f"{min_val:<10.3f}{variance:<12.3f}{std_dev:<10.3f}{length:<6}"
        )
        ax = axes[row][col]
        ax.plot(data)
        ax.set_title(label)
        ax.set_xlabel("Index")
        ax.set_ylabel("Value")

        if label == "trace_mcu":
            peaks, properties = find_peaks(np.array(data), height=0.5, distance=500, width=1, prominence=0.5)
            spike_widths = [int(w) for w in properties["widths"]]
            peak_heights = [round(float(data[p]), 3) for p in peaks]
            #peak_positions = [int(p) for p in peaks]
            peak_positions = [int(i) for i, v in enumerate(data) if v > 1.5][:21]

            # Extract last spike from trace_mcu
            if len(peaks) > 0:
                last_peak = peaks[-1]
                threshold = 1
                padding = 20

                start = last_peak
                while start > 0 and data[start] > threshold:
                    start -= 1

                end = last_peak
                while end < len(data) - 1 and data[end] > threshold:
                    end += 1

                start = max(0, start - padding)
                end   = min(len(data), end + padding)
                last_spike_data = list(data[start:end])
                print(start)
                print(end)
                last_spike_range = (start, end)  # save for led overlay
            

    # After the loop, build the overlay using trace_led_auth's drop as anchor
    ax_spike = axes[0][2]

    led_data = np.array(traces["trace_led_auth"])
    mcu_data = np.array(traces["trace_mcu"])

    # Find where trace_led_auth drops (falls below mid-point)
    led_mid = (np.max(led_data) + np.min(led_data)) / 2
    drop_indices = np.where(led_data < led_mid)[0]

    if len(drop_indices) > 0:
        padding = 50
        anchor = drop_indices[0]  # just use the start of the drop
        start = max(0, anchor - padding)
        end   = min(len(led_data), anchor + padding)
        ax_spike.plot(mcu_data[start:end], label="trace_mcu", alpha=0.8)
        ax_spike.plot(led_data[start:end], label="trace_led_auth", alpha=0.8, color="orange")

    ax_spike.set_title("Last Spike (trace_mcu + trace_led_auth)")
    ax_spike.set_xlabel("Sample")
    ax_spike.set_ylabel("Value")
    ax_spike.legend()

    # Bottom-middle: bar chart of all peak heights
    ax_peaks = axes[1][1]
    if peak_heights:
        ax_peaks.bar(range(len(peak_heights) - 1), peak_heights[:-1], width=0.6)
        ax_peaks.set_title("Peak Heights (trace_mcu)")
        ax_peaks.set_xlabel("Spike #")
        ax_peaks.set_ylim(min(peak_heights[:-1]) - 0.01, max(peak_heights[:-1]) + 0.01)
        ax_peaks.set_ylabel("Height")

    # Bottom-right: stats + spike widths
    ax_stats = axes[1][2]
    ax_stats.axis("off")
    stats_lines.append("")
    stats_lines.append("Spike widths (trace_mcu):")
    stats_lines.append(str(spike_widths))
    stats_lines.append("")
    stats_lines.append("Spike positions (trace_mcu):")
    stats_lines.append(str(peak_positions)) 
    ax_stats.text(
        0.01, 0.95, "\n".join(stats_lines),
        transform=ax_stats.transAxes,
        fontsize=8,
        verticalalignment="top",
        fontfamily="monospace",
        bbox=dict(boxstyle="round", facecolor="lightyellow", alpha=0.8)
    )
    plt.tight_layout()
    plt.show()


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

        #print(traces.keys())
        #print(traces["trace_led_auth"])
        #print(traces["trace_led_unlocked"])
        #print(traces["trace_mcu"])
        
        
        #printtrace(traces, password)
        peak_positions = [int(i) for i, v in enumerate(traces["trace_mcu"]) if v > 1.5][:21]
        
        return traces, peak_positions

def challenge_response():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as conn:
        conn.connect((HOST, PORT))

        # consume text
        banner = socket_readline(conn)
        print(banner.decode())

        # consume text
        req = socket_readline(conn)
        print(req.decode())

        # There was a print() around this, I removed it
        conn.recv(1024).strip()
        
        conn.send(b'auth')
        
        mobileauth = conn.recv(1024).strip()
        print(mobileauth)
        mcmd = conn.recv(1024).strip()
        print(mcmd)
        #conn.send(b'00000\n')
        conn.send(b'getChallenge')
        challenge_text = conn.recv(1024).strip()
        print(challenge_text)
        challenge_bytes = challenge_text[6:]
        print("Challenge: {}".format(challenge_bytes))
        mcmd = conn.recv(1024).strip()
        print(mcmd)
        sha1_hash = hashlib.sha1(challenge_bytes + SECRET).hexdigest()
        sha1_response = b'resp:' + challenge_bytes + b":" + sha1_hash.encode()
        print("Challenge response: {}".format(sha1_response))
        conn.send(sha1_response)
        authenticated = conn.recv(1024).strip()
        print(authenticated)
        passcode = conn.recv(1024).strip()
        print(passcode)
        conn.send(PASSWORD)
        authenticated = conn.recv(1024).strip()
        print(authenticated)
        authenticated = conn.recv(1024).strip()
        print(authenticated)
        authenticated = conn.recv(1024).strip()
        print(authenticated)
        

        # TODO - once we have the passcode, send it as well, probably retrieve the flag after this



challenge_response()

# chars = list(string.ascii_letters + string.digits)
# peak_position_list = []
# password = ""

# for i in range(20):
#     for digit in list(string.digits):
#         password_candidate = digit
#         traces, peak_positions = send_password(password + password_candidate)
#         peak_position_list.append(peak_positions)
#     for dig, peak in enumerate(peak_position_list):
#         print("Iter: {} Digit: {}\nPeaks: {}".format(i, dig, peak)) 
#     peaks_of_interest = [peak[2 + i] for peak in peak_position_list]
#     print("Peaks of interest: \n{}".format(peaks_of_interest))
#     counts = Counter(peaks_of_interest)
#     outlier_val = [val for val, count in counts.items() if count == 1][0]
#     outlier = peaks_of_interest.index(outlier_val) # This is our digit to the password!
#     password = password + str(outlier)
#     print("##### PASSWORD VALUE FOUND #####\n Password: {} \n #########################".format(password))
#     peak_position_list = []

# trace_list = []
# temp = []
# #for i in range(10):
# for digit in list(string.digits):
#     for i in range(5): # Do this 5 times each, 50 total
#         password_candidate =  digit
#         temp.append(send_password(password_candidate))
#     trace_list.append(temp)
#     temp = []