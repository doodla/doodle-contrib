# Increase Swap to 1GB
# Run as root or with sudo
dd if=/dev/zero of=/var/swap bs=1k count=1024k
mkswap /var/swap
swapon /var/swap
echo '/var/swap swap swap default 0 0' >> /etc/fstab
