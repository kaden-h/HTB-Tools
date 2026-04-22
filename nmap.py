#!/usr/bin/python3
import sys
import subprocess
import time

try:
    ip = sys.argv[1]
except IndexError:
    print("Usage: sudo {} [ip]".format(sys.argv[0]))
    print("ip: IP address of the target")
    exit(0)

print("Making nmap directory...")
mkdir = subprocess.Popen(["mkdir", "nmap"])
time.sleep(1)

print("Scanning (quick)...")
nmap_quick = subprocess.Popen(["nmap", "-sC", "-sV", str(ip), "-oA", "nmap/tcp_quick", "-v"])
input("Waiting for nmap quick scan to complete... Press enter to run full scan")
nmap_quick.terminate()
nmap_full = subprocess.Popen(["nmap", "-sC", "-sV", "-p-", str(ip), "-oA", "nmap/tcp_full", "-v"])
input("Waiting for nmap full scan to complete... Press enter to run UDP scan")
nmap_full.terminate()
nmap_udp = subprocess.Popen(["nmap", "-sU", "--min-rate", "10000", "-p-", str(ip), "-oA", "nmap/udp_full", "-v"])
input("Waiting for nmap UDP scan to complete... Press enter to exit")


print()
print("#################################################")
print("### This script is kinda scuffed, but it will ###")
print("### work as intended for the most part.       ###")
print("### manual toggle because sometimes windows   ###")
print("### will hang on the full scan.               ###")
print("### Made with <3 and >:3 by Kaden H           ###")
print("#################################################")
print()
