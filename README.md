# Harrogate Cleaners website

Static website for Harrogate Cleaners, 34 Cold Bath Road, Harrogate HG2 0NA.

- The site is the HTML files, `images/`, `sitemap.xml`, `robots.txt` and `llms.txt` in this folder. Upload them to the web root (`public_html` on Hostinger).
- `_source/build.py` regenerates every page. Edit the settings at the top (domain, hours, WhatsApp, Google review link, Zoho chat code), then run `python3 _source/build.py` and copy the files from `_source/out/deploy/` here.
