
import os

def setup_cahicha():
    """
    Interactive setup function for CAHICHA configuration.
    Returns a dictionary with configuration settings or None if setup is terminated.
    """
    config = {}
    
    def get_yes_no_input(prompt, ideal=None, error_msg=None):
        """Helper function to get Y/n input with validation."""
        while True:
            response = input(prompt).strip().lower()
            if response == '':
                response = 'y'  # Default to yes if empty
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                print("Please enter Y/y/yes or N/n/no")
    
    # Step 1: Initial setup confirmation
    print("Do you want to setup CAHICHA? (Y/n) (ideal=Y)")
    setup_confirm = get_yes_no_input("")
    if not setup_confirm:
        print("Error: Setup terminated")
        return None
    
    # Step 2: Server hosting location
    print("\nIs the website hosted on Current server? (Y/n)")
    current_server = get_yes_no_input("")
    
    if current_server:
        config['host'] = 'localhost'
        print("[Set host=localhost]")
        
        # Step 2a: Port configuration for current server
        print("\nIs the website hosted on default port 80 or 443? (Y/n) (ideal=N)")
        default_port = get_yes_no_input("")
        if default_port:
            print("Error: Website needs to be on non-standard port")
            return None
        
        # Get custom port
        port_input = input("Which port is it hosted in? (default=8080): ").strip()
        if port_input == '':
            config['port'] = 8080
        else:
            try:
                config['port'] = int(port_input)
            except ValueError:
                print("Error: Port must be a valid number")
                return None
        print(f"[Set port={config['port']}]")
        
    else:
        # Step 2b: External host configuration
        host_input = input("What is the host IP? ").strip()
        if not host_input:
            print("Error: Host IP cannot be empty")
            return None
        config['host'] = host_input
        print(f"[Set host={config['host']}]")
        
        port_input = input("What is the host port? (Default=80): ").strip()
        if port_input == '':
            config['port'] = 80
        else:
            try:
                config['port'] = int(port_input)
            except ValueError:
                print("Error: Port must be a valid number")
                return None
        print(f"[Set port={config['port']}]")
    
    # Step 3: TLS configuration check
    print("\nDoes the website already have TLS configuration? (Y/n) (ideal=n)")
    has_tls = get_yes_no_input("")
    if has_tls:
        print("Error: TLS needs to be configured after setup. Remove TLS and try again")
        return None
    
    # Step 4: Domain name check
    print("\nDoes this current server have associated domain name? (Y/n) (ideal=Y)")
    has_domain = get_yes_no_input("")
    if not has_domain:
        print("Error: Domain name is required")
        return None
    
    # Get domain name
    domain_input = input("What is the domain name? ").strip()
    if not domain_input:
        print("Error: Domain name cannot be empty")
        return None
    config['domainname'] = domain_input
    print(f"[Set domainname={config['domainname']}]")
    
    # Step 5: Port 5000 availability check
    print("\nIs port 5000 being used? (Y/n) (ideal=n)")
    port_5000_used = get_yes_no_input("")
    if port_5000_used:
        print("Error: Port 5000 needs to be free")
        return None
    
    # Step 6: TLS certificates availability
    print("\nDo you have TLS certs ready? (Y/n) (ideal=Y)")
    tls_ready = get_yes_no_input("")
    print("Warn: TLS needs to be added after the setup for this to be functional")
    if not tls_ready:
        config['tlsavailable'] = False
    else:
        config['tlsavailable'] = True
    print(f"[Set tlsavailable={config['tlsavailable']}]")
    
    return config

def change_file(config, filepath):
    text=''
    if '.git' in str(filepath):
        return
    with open(filepath, 'r') as file:
        text=file.read()
    for key, value in config.items():
        text=text.replace(f'$${key}$$', str(value))
    with open(filepath, 'w') as file:
        file.write(text)


from pathlib import Path

def initport():
    text=''
    with open('/etc/apache2/ports.conf', 'r') as file:
        text=file.read()
    if not 'Listen 5000' in text:
        with open('/etc/apache2/ports.conf', 'a') as file:
            file.write('\nListen 5000\n')
    if not ('Listen 80 ' in text or 'Listen 80\n' in text):
        with open('/etc/apache2/ports.conf', 'a') as file:
            file.write('\nListen 80\n')

def list_all_files(folder_path, config):
    """
    Print absolute paths of all files in the given folder and its subdirectories.
    
    Args:
        folder_path (str): Path to the folder to scan
    """
    try:
        # Convert to Path object and resolve to absolute path
        folder = Path(folder_path).resolve()
        
        # Check if folder exists
        if not folder.exists():
            print(f"Error: Folder '{folder_path}' does not exist.")
            return
        
        # Check if it's actually a directory
        if not folder.is_dir():
            print(f"Error: '{folder_path}' is not a directory.")
            return
        
        print(f"Scanning folder: {folder}")
        print("-" * 50)
        
        file_count = 0
        
        # Walk through all files recursively
        for file_path in folder.rglob('*'):
            if file_path.is_file():
                print(file_path)
                try:
                    change_file(config, file_path)
                except:
                    pass
                file_count += 1
        
        print("-" * 50)
        
    except PermissionError:
        print(f"Error: Permission denied accessing '{folder_path}'")
    except Exception as e:
        print(f"Error: {e}")
    
def perform_setup(config):
    os.system('sudo apt-get update')
    os.system('sudo apt-get install apache2 python3 python3-pip python3-flask python3-cryptography git')
    os.system('sudo python3 -m pip install fido2 --break-system-packages')
    os.system('sudo apt-get install libapache2-mod-wsgi-py3')
    os.system('mkdir -p /var/cahicha')
    os.system('touch /var/cahicha/test')
    os.system('chown -R www-data:www-data /var/cahicha')
    os.system('chmod -R 777 /var/cahicha')
    try:
        os.system('rm -rf cahicha')
    except:
        pass
    os.system('git clone https://github.com/AdityaMitra5102/cahicha')
    list_all_files('./cahicha', config)
    initport()
    os.system('sudo a2enmod rewrite')
    os.system('sudo a2enmod proxy')
    os.system('sudo a2enmod proxy_http')
    os.system('cp -r ./cahicha/sites-enabled /etc/apache2/')
    os.system('cp -r ./cahicha/www /var/')
    os.system('sudo chmod 777 /etc/apache2/sites-enabled/*')
    os.system('sudo chown -R www-data:www-data /var/www')
    os.system('sudo chmod -R 777 /var/www')
    os.system('sudo service apache2 restart')   


def main():
    """Main function to run the CAHICHA setup."""
    print("=== CAHICHA Setup Script ===\n")
    
    config = setup_cahicha()
    
    if config is None:
        print("\nSetup was terminated due to errors.")
        return
    
    print("\n=== Setup Complete! ===")
    print("Configuration Summary:")
    for key, value in config.items():
        print(f"  {key}: {value}")

    perform_setup(config)


if __name__ == "__main__":
    main()
