# ZapCodeAutoActivator
Automatically activates zap-hosting.com codes for balance. (Login needed for cookie capcture)

# THE PROGRAM REQUIRES HTTP PROXY TO USE (username:passoword@ip:port format, in the current version it works the best with rotating proxy so you can activate as mutch account as you want.) 
-# I will create a version without need of proxies

# How to setup?
1. Download the files.
  1.a Install python (latest) ONLY if you dont have.
  1.b Put your zaphosting codes to the coupons.txt (1 per line)
  1.c Run the following commands in the folder of the downloaded files:
      - pip install -r requriements.txt
      - python main.py
3. Log in to your zap hosting account in the popup chrome window.
4. Wait until the code activates the codes on your account.
5. IF you have multiple accounts the program will ask you about it (press y and enter if you have and want to activate on those too. In that case repeat from the point 3.

# Troubleshooting guide
- If you stuck on cloudflare captcha, just open an other windows, go to https://zap-hosting.com/ complete chapctha, go back to the first tab, do the capctha and done. You can log in now. (DO NOT use another windows to login otherwise it will fail to get cookies)
