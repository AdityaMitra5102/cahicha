# CAHICHA
## Completely Automated Hardware Interaction test to tell Computers and Humans Apart



## Setup:

Step 1: Set up your website as you would do normally, with any web server like apache2, nginx, gunicorn, express, pm2 etc.

Step 2: Do not set up TLS on your website and host it on a non-standard port like 8080. Ensure that this port is blocked via firewall and not accessible externally.

Step 3: Ensure you have a mapped DNS. This does not work without a domain name.

Step 4: Run the setup script as below.

```
wget https://adityamitra5102.github.io/cahicha/setup.py
sudo python3 setup.py
```

Step 5: Setup TLS. You may use Certbot or any other tool, or even set up manually. If doing manually, set it up only on 001-default.conf on apache2. Ensure it is serving on port 443 after adding TLS.

Thus, CAHICHA can be set up on any website without any changes in the website itself, and yet protect it from scrapers and bots.


⚠️ Do note that this setup works for only Ubuntu and Debian based web servers. For others, you may modify the setup scripts accordingly. 