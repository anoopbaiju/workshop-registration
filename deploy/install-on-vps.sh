#!/usr/bin/env bash
# Run on the VPS as root after copying workshop-registration to /root/workshop-registration
set -euo pipefail

APP_DIR=/root/workshop-registration
PORT=8080

echo "==> Python venv + dependencies"
cd "$APP_DIR"
python3 -m venv venv
./venv/bin/pip install -r requirements.txt

echo "==> systemd service"
cp deploy/workshop-registration.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable workshop-registration
systemctl restart workshop-registration
systemctl --no-pager status workshop-registration

echo "==> nginx site"
cp deploy/nginx-register.conf /etc/nginx/sites-available/register.dhruvscreations.com
ln -sf /etc/nginx/sites-available/register.dhruvscreations.com /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx

echo ""
echo "Done. App listens on 127.0.0.1:$PORT"
echo "Next: point register.dhruvscreations.com DNS to this server's IP"
echo "Then: certbot --nginx -d register.dhruvscreations.com"
