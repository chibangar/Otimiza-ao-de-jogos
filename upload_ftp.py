import os
import ftplib
import sys

FTP_HOST = "ftpupload.net"
FTP_USER = "if0_42649705"
FTP_PORT = 21

def upload_dir(ftp, local_dir, remote_dir):
    print(f"Uploading {local_dir} to {remote_dir}...")
    try:
        ftp.cwd(remote_dir)
    except ftplib.error_perm:
        ftp.mkd(remote_dir)
        ftp.cwd(remote_dir)
    
    for item in os.listdir(local_dir):
        local_path = os.path.join(local_dir, item)
        if os.path.isfile(local_path):
            print(f"Uploading file: {item}")
            with open(local_path, "rb") as fp:
                ftp.storbinary(f"STOR {item}", fp)
        elif os.path.isdir(local_path):
            print(f"Entering directory: {item}")
            upload_dir(ftp, local_path, f"{remote_dir}/{item}")
            ftp.cwd(remote_dir)

def main():
    if len(sys.argv) < 2:
        print("Usage: py upload_ftp.py <PASSWORD>")
        sys.exit(1)
    
    password = sys.argv[1]
    local_htdocs = r"C:\Users\Chibanga\Documents\Otimiza-ao-de-jogos-main\htdocs"
    
    print(f"Connecting to {FTP_HOST} as {FTP_USER}...")
    ftp = ftplib.FTP()
    ftp.connect(FTP_HOST, FTP_PORT, timeout=30)
    ftp.login(FTP_USER, password)
    print("Connected and logged in successfully!")
    
    # Destination is /htdocs
    upload_dir(ftp, local_htdocs, "/htdocs")
    ftp.quit()
    print("ALL FILES UPLOADED SUCCESSFULLY!")

if __name__ == "__main__":
    main()
