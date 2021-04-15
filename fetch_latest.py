import subprocess

import matplotlib.pyplot as plt
from obspy import UTCDateTime, read
from obspy.clients.fdsn import Client

# Station and channel info (edit me!)
STATION = 'RAF63'
CHANNEL = 'EHZ'

# For converting to local time (edit me!)
UTC_OFFSET = -8

# Create URL for downloading via FTP
now = UTCDateTime()
base_url = f'ftp://rs.local/{now.year}/AM/{STATION}/{CHANNEL}.D/'
filename = f'AM.{STATION}.00.{CHANNEL}.D.{now.year}.{now.julday:03}'

# Download most recent miniSEED file (Python's requests library can't do FTP)
print(f'Downloading {filename}')
subprocess.call(['curl', '--remote-name', '--silent', base_url + filename])
print('Done')

# Read in and remove response, detrend, merge
st = read(filename)
inventory = Client('RASPISHAKE').get_stations(
    network='AM', station=STATION, channel=CHANNEL, level='response'
)
st.remove_response(inventory)
st.detrend('demean')
st.merge(fill_value=0)

# Change to local time
for tr in st:
    tr.stats.starttime += UTC_OFFSET * 60 * 60

# Make interactive plot
fig = plt.figure(figsize=(10, 4))
st.plot(method='full', fig=fig)
ax = fig.axes[0]
sign = '$+$' if UTC_OFFSET >= 0 else '$-$'
ax.set_xlabel(f'UTC {sign} {abs(UTC_OFFSET)} hrs')
ylabel = 'Acceleration (m/s$^2$)' if CHANNEL[1] == 'N' else 'Velocity (m/s)'
ax.set_ylabel(ylabel)
fig.tight_layout()
plt.show()
