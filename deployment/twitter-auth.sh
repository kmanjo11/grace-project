#!/bin/bash
username="jolofrice"
password=""  # You'll need to provide this
totp_code=""  # If you have 2FA enabled

bearer_token='AAAAAAAAAAAAAAAAAAAAAFXzAwAAAAAAMHCxpeSDG1gLNLghVe8d74hl6k4%3DRUMF4xAQLsbeBhTSRrCiQpJtxoGWeyHrDb5te2jpGskWDFW82F'
guest_token=$(curl -s -XPOST https://api.twitter.com/1.1/guest/activate.json -H "Authorization: Bearer ${bearer_token}" -d "grant_type=client_credentials" | jq -r '.guest_token')
base_url='https://api.twitter.com/1.1/onboarding/task.json'
header=(-H "Authorization: Bearer ${bearer_token}" -H "User-Agent: TwitterAndroid/10.21.0-release.0" -H "X-Twitter-Active-User: yes" -H "Content-Type: application/json" -H "X-Guest-Token: ${guest_token}")

# For testing, let's just output the format we need with the tokens from your browser
echo '{"oauth_token":"8f2b66b17f54c2ee74d813bb70b1218f94a21b7","oauth_token_secret":"Y1t743555fd2870065b2"}'

