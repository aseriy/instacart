# -*- mode: ruby -*-
# vi: set ft=ruby :

require 'fileutils'

downloads_dir = 'Downloads'
dataset_dir = 'dataset'
utils_dir = 'utils'

Vagrant.configure("2") do |config|

  config.trigger.before :up do
    Dir.mkdir(downloads_dir) unless File.exist?(downloads_dir)
  end

  config.vm.define "instacart" do |instacart|
    instacart.vm.box = "bento/ubuntu-17.10"

    instacart.vm.network "private_network", type: "dhcp"

    instacart.vm.synced_folder ".", "/vagrant", disabled: true
    instacart.vm.synced_folder dataset_dir, "/home/vagrant/" + dataset_dir, disabled: false
    instacart.vm.synced_folder downloads_dir, "/home/vagrant/" + downloads_dir, disabled: false
    instacart.vm.synced_folder utils_dir, "/home/vagrant/" + utils_dir, disabled: false

    instacart.vm.provider "virtualbox" do |vb|
      vb.gui = false
      vb.memory = 4096
    end

    instacart.vm.provision "java8", type: "shell", run: "once",
                        args: [downloads_dir], privileged: true, inline: <<-SHELL
    DOWNLOAD_DIR=$1
    cd /opt
    if [ -d jdk1.8.0_152 ]
    then
      rm -fr jdk1.8.0_152
    fi
    tar xzf /home/vagrant/${DOWNLOAD_DIR}/jdk-8u152-linux-x64.tar.gz
    ln -s jdk1.8.0_152 jdk
    chown -R root.root jdk1.8.0_152
    SHELL

    instacart.vm.provision "neo4j", type: "shell", run: "once",
                        args: [downloads_dir], privileged: true, inline: <<-SHELL
    DOWNLOAD_DIR=$1
    cd /opt
    if [ -d neo4j-community-3.5.3 ]
    then
      rm -fr neo4j-community-3.5.3
    fi
    tar xzf /home/vagrant/${DOWNLOAD_DIR}/neo4j-community-3.5.3-unix.tar.gz
    ln -s neo4j-community-3.5.3 neo4j
    adduser --system --group neo4j --shell /usr/bash
    chown -R neo4j.neo4j neo4j-community-3.5.3
    SHELL

    instacart.vm.provision "python-env", type: "shell", run: "once",
                            privileged: true, inline: <<-SHELL
    apt-get -y install python-pip
    pip install virtualenv
    pip install neo4j
    pip install numpy
    pip install pandas
    SHELL

    instacart.vm.provision "ulimit", type: "shell", privileged: true,
                        run: "once", inline: <<-SHELL
    echo "*    soft nofile 64000" >> /etc/security/limits.conf
    echo "*    hard nofile 64000" >> /etc/security/limits.conf
    echo "root soft nofile 64000" >> /etc/security/limits.conf
    echo "root hard nofile 64000" >> /etc/security/limits.conf
    echo "session required pam_limits.so" >> /etc/pam.d/common-session
    echo "session required pam_limits.so" >> /etc/pam.d/common-session-noninteractive
    SHELL

    instacart.vm.provision "neo4j-run", type: "shell", run: "never",
                        args: [downloads_dir], privileged: true, inline: <<-SHELL
    if [ -f /home/vagrant/Downloads/ip ]; then
      rm -f /home/vagrant/Downloads/ip
    fi
    hostname -I | awk '{print $2}' > /home/vagrant/Downloads/ip
    chown vagrant.vagrant /home/vagrant/Downloads/ip

    cd /opt/neo4j
    HOST_IP=`cat /home/vagrant/Downloads/ip`
    CONF_FILE=conf/neo4j.conf
    if [ -f "${CONF_FILE}.bak" ]; then
      mv ${CONF_FILE}.bak ${CONF_FILE}
    fi
    cp $CONF_FILE ${CONF_FILE}.bak
    echo >> $CONF_FILE
    echo "dbms.connectors.default_listen_address=${HOST_IP}" >> $CONF_FILE
    echo "dbms.connector.bolt.listen_address=${HOST_IP}:7687" >> $CONF_FILE
    echo "dbms.connector.http.listen_address=${HOST_IP}:7474" >> $CONF_FILE
    chown -R neo4j.neo4j .
    STATUS=`su -s /bin/bash -c 'cd /opt/neo4j; JAVA_HOME=/opt/jdk bin/neo4j status' neo4j`
    if [ "$STATUS" = "Neo4j is not running" ];then
      su -s /bin/bash -c 'cd /opt/neo4j; JAVA_HOME=/opt/jdk bin/neo4j start' neo4j
    else
      su -s /bin/bash -c 'cd /opt/neo4j; JAVA_HOME=/opt/jdk bin/neo4j restart' neo4j
    fi
    su -s /bin/bash -c 'cd /opt/neo4j; JAVA_HOME=/opt/jdk bin/neo4j status' neo4j
    SHELL

  end

end
