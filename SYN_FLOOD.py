from scapy.all import *
from scapy.layers.dns import *

# create (or open if exists) text file to write attackers' IP
attackersListFile = open('attackersListFiltered.txt', 'w')

# open pcap file
pcapFile = rdpcap("SynFloodSample.pcap")
print('Opened')
print("Checking packets...")

# flags hex values
SYN = 0x02
ACK = 0x10
NORMAL_RTT = 0.0041  # 0.0001 for sending the packet, 0.002 for the packet to pass, multiplied by 2.
suspicion_level_dict = {}  # was made for sorting suspicious IP addresses by the amount of times their delta wasn't big enough
syn_ack_packets = {}
# condition - syn ack without ack
for pkt in pcapFile:
    if TCP in pkt:
        if pkt[TCP].flags == SYN + ACK:  # we got syn ack, I'll remember that, let's check if we got an ack.
            if pkt[IP].dst not in syn_ack_packets:
                syn_ack_packets[pkt[IP].dst] = 1
            else:
                syn_ack_packets[pkt[IP].dst] += 1
        if pkt[TCP].flags == ACK:  # feew, he's okay
            if pkt[IP].dst in syn_ack_packets:
                syn_ack_packets[pkt[IP].dst] -= 1
                if syn_ack_packets[pkt[IP].dst] == 0:  # cleaning the dictionary
                    syn_ack_packets.pop(pkt[IP].dst)

for key, value in syn_ack_packets.items():  # adding the addresses and their suspicion level to the dict
    suspicion_level_dict[key] = value

# condition - fast syns
ack_packets = {}
for pkt in pcapFile:
    if TCP in pkt:
        if pkt[TCP].flags == SYN:
            # check if IP in dict
            if pkt[IP].src not in ack_packets:  # no -
                ack_packets[pkt[IP].src] = pkt.time  # update dict value
            else:  # yes - check if delta time is big enough
                if pkt.time - ack_packets[pkt[IP].src] < NORMAL_RTT:  # not big enough - suspicious IP
                    if pkt[IP].src not in suspicion_level_dict:
                        suspicion_level_dict[pkt[IP].src] = 1
                    else:
                        suspicion_level_dict[pkt[IP].src] += 1
                else:  # big enough - update dict value
                    ack_packets[pkt[IP].src] = pkt.time
suspicion_level_dict = dict(sorted(suspicion_level_dict.items(), key=lambda item: item[1]))  # sort dict by value
attackersListFile.write("List of IP addresses, sorted by level of suspicion:\n\t")
for key, value in suspicion_level_dict.items():
    attackersListFile.write(key + '\n\t')
attackersListFile.close()
print("Done!")
