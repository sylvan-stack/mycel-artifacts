---
role: authored
---
# Places API log server (SFTP)

The places-api log server keeps Reservble's integration logs as daily files and serves them over read-only SFTP. The [Places API Logs guide](../operations/places-api-logs.md) owns the investigation workflow; this manual covers the connection and the commands. Examples use placeholders: the actual values stay in the local credential file and never go into this corpus.

## Connection settings

All values live in `~/repos/Reservble/places-api/.settings/credentials.env`. Git ignores it through the places-api `.settings` rule, and its mode is `600`.

| Key | Holds |
|---|---|
| `RESERVBLE_SFTP_HOST` | server address |
| `RESERVBLE_SFTP_PORT` | port, normally `22` |
| `RESERVBLE_SFTP_USER` | account name |
| `RESERVBLE_SFTP_DIR` | log directory, `/webhooks`: the directory the login opens in |
| `RESERVBLE_SFTP_HOST_FINGERPRINT` | expected ED25519 host key fingerprint, `SHA256:<base64>` |
| `RESERVBLE_SFTP_PASSWORD` | password |

Read the values with a dotenv parser with interpolation disabled; never source the file as shell code or display it. `RESERVBLE_SFTP_PASSWORD` may also be supplied as a runtime environment variable. The places-api application's `.env` is not the source of these values.

## Verify the host key

Scan the server's keys into a scratch directory and keep only the key whose fingerprint equals `RESERVBLE_SFTP_HOST_FINGERPRINT`:

```sh
ssh-keyscan -p <port> <host> 2>/dev/null > <scratch>/scanned_hosts
: > <scratch>/known_hosts
while IFS= read -r line; do
  fp=$(printf '%s\n' "$line" | ssh-keygen -l -f - 2>/dev/null | awk '{print $2}')
  [ "$fp" = "<fingerprint>" ] && printf '%s\n' "$line" >> <scratch>/known_hosts
done < <scratch>/scanned_hosts
```

An empty `<scratch>/known_hosts` means no key matched: stop and report it. Never trust the scanned keys without this comparison.

## Sign in on this Mac

The system curl on macOS has no SFTP support. Unattended access works with OpenSSH `sftp` and an `SSH_ASKPASS` helper that hands over the password only when asked for one. Keep the helper outside any download directory, with mode `700`:

```python
#!/usr/bin/env -S python3 -I
import os, sys

FILE = os.path.expanduser("~/repos/Reservble/places-api/.settings/credentials.env")

if "password" not in (sys.argv[1] if len(sys.argv) > 1 else "").lower():
    sys.exit(1)
password = os.environ.get("RESERVBLE_SFTP_PASSWORD")
if not password:
    with open(FILE, encoding="utf-8") as f:
        for line in f:
            key, sep, value = line.strip().partition("=")
            if sep and key.strip() == "RESERVBLE_SFTP_PASSWORD":
                password = value.strip().strip("'\"")
if not password:
    sys.exit(1)
print(password)
```

Pipe the commands to `sftp` on stdin. Do not use `-b`: it sets `BatchMode`, which disables password authentication. Without `-b` a failed command does not end the session, so check the output for errors.

```sh
printf 'ls -l /webhooks/*_<YYYY-MM-DD>*\nbye\n' |
  SSH_ASKPASS=<helper> SSH_ASKPASS_REQUIRE=force DISPLAY=:0 \
  sftp -q -P <port> -F /dev/null \
    -o UserKnownHostsFile=<scratch>/known_hosts -o GlobalKnownHostsFile=/dev/null \
    -o StrictHostKeyChecking=yes -o HostKeyAlgorithms=ssh-ed25519 \
    -o PubkeyAuthentication=no -o PreferredAuthentications=password,keyboard-interactive \
    -o NumberOfPasswordPrompts=1 -o ConnectTimeout=15 \
    <user>@<host>
```

`get /webhooks/<file> <scratch>/<file>` downloads a file in the same way. `ls -l` in `sftp` shows modification times in the Mac's local time zone, not UTC.

## Interactive sign-in

```text
sftp -P <port> <user>@<host>
# Check the displayed fingerprint against RESERVBLE_SFTP_HOST_FINGERPRINT before accepting.
sftp> ls /webhooks/syrve_plugin_rejected_*
sftp> get /webhooks/syrve_plugin_rejected_<YYYY-MM-DD>.log <scratch>/rejected.log
sftp> bye
```

## curl with SFTP support

Check `curl --version` for `sftp` among its protocols before choosing curl. Pin the host with `--hostpubsha256 '<fingerprint without the SHA256: prefix>'` or a verified known-hosts entry. Supply the password through a permission-restricted curl config or stdin, never in process arguments, and do not enable verbose credential logging.

```text
# List filenames:
curl --show-error --fail --list-only sftp://<host>/webhooks/
# Selected daily file:
curl --show-error --fail sftp://<host>/webhooks/syrve_plugin_rejected_<YYYY-MM-DD>.log
# Last approximately 2 MB of the large Cloud API log:
curl --show-error --fail --range -2000000 sftp://<host>/webhooks/syrve_<YYYY-MM-DD>.log
```

Check transfer success before interpreting an empty result; avoid pipelines that conceal download errors.
