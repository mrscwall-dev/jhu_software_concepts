# Module 2 - Web Scraping Assignment

## robots.txt Compliance

Before scraping GradCafe, I reviewed the site's robots.txt file. The general `User-agent: *` rule allows access to `/`, while account-related paths such as `/signin`, `/register`, `/forgot-password`, `/reset-password`, `/confirm-password`, `/verify-email`, and `/profile` are disallowed.

This project will access only publicly available GradCafe applicant-result pages. It will not access disallowed paths, bypass login requirements, CAPTCHAs, rate limits, Cloudflare restrictions, or other access controls. The scraper will use reasonable delays and will stop if the website blocks, rate-limits, or rejects requests.

Evidence of the robots.txt review is included as `screenshot.jpg`.