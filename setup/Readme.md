# Setup Workoutizer

**NOTE: Setup on a Raspberry Pi is still in development**

Follow these instructions to install Workoutizer on a Raspberry Pi:

### Setup Pi using Ansible

Modify the `hosts` file by entering the ip address of your pi. (Use [nmap](https://nmap.org/) to determine it)

Open the `config.ini` file and adjust the the given parameters to your corresponding values.

Run the ansible playbook

```shell script
ansible-playbook -i hosts setup_workoutizer.yml
```
