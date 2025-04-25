import yaml
import os

CONFIG_FILE = "/app/config.yaml"
SUPERVISOR_DIR = "/etc/supervisor/conf.d"

def sanitize(name):
    return name.replace(" ", "_").lower()

def create_supervisor_program(name, input_url, output_url):
    program_name = sanitize(name)
    log_out = f"/var/log/{program_name}.out.log"
    log_err = f"/var/log/{program_name}.err.log"

    gst_command = ""
    if input_url.startswith("srt://"):
        gst_command = (
            f"gst-launch-1.0 -v srtserversrc uri={input_url}?mode=listener ! "
            f"tsparse alignment=7 ! queue max-size-buffers=0 max-size-time=0 max-size-bytes=10000000 ! "
            f"identity sync=true ! mpegtsmux ! "
            f"udpsink host={output_url.split('//')[1].split(':')[0]} port={output_url.split(':')[-1]} ttl=4"
        )
    elif output_url.startswith("srt://"):
        gst_command = (
            f"gst-launch-1.0 -v udpsrc address={input_url.split('//')[1].split(':')[0]} "
            f"port={input_url.split(':')[-1]} buffer-size=5000000 caps=\"video/mpegts, systemstream=(boolean)true, packetsize=(int)188\" ! "
            f"tsparse alignment=7 ! queue max-size-buffers=0 max-size-time=0 max-size-bytes=10000000 ! "
            f"identity sync=true ! "
            f"srtsink uri={output_url}?mode=caller"
        )
    else:
        gst_command = (
            f"gst-launch-1.0 -v udpsrc address={input_url.split('//')[1].split(':')[0]} "
            f"port={input_url.split(':')[-1]} buffer-size=5000000 caps=\"video/mpegts, systemstream=(boolean)true, packetsize=(int)188\" ! "
            f"tsparse alignment=7 ! queue max-size-buffers=0 max-size-time=0 max-size-bytes=10000000 ! "
            f"identity sync=true ! "
            f"udpsink host={output_url.split('//')[1].split(':')[0]} port={output_url.split(':')[-1]} ttl=4"
        )  # Optimized for KLV (STANAG 4609) MPEG-TS passthrough

    return f"""
[program:{program_name}]
command={gst_command}
autostart=true
autorestart=true
stdout_logfile={log_out}
stderr_logfile={log_err}
stdout_logfile_maxbytes=10MB
stdout_logfile_backups=5
stderr_logfile_maxbytes=10MB
stderr_logfile_backups=5
"""

def main():
    with open(CONFIG_FILE, 'r') as f:
        config = yaml.safe_load(f)

    existing = set(os.listdir(SUPERVISOR_DIR))
    new_streams = set()

    for stream in config['streams']:
        name = stream['name']
        output = stream['output']
        input_ = stream['input']
        conf = create_supervisor_program(name, input_, output)
        filename = f"{sanitize(name)}.conf"
        new_streams.add(filename)
        full_path = os.path.join(SUPERVISOR_DIR, filename)

        if not os.path.exists(full_path) or open(full_path).read() != conf:
            with open(full_path, 'w') as out:
                out.write(conf)

    for old in existing:
        if old.endswith(".conf") and old not in new_streams and not old.startswith("healthcheck"):
            os.remove(os.path.join(SUPERVISOR_DIR, old))

if __name__ == "__main__":
    main()