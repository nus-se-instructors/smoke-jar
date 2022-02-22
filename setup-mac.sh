git clone git@github.com:XQuartz/xorg-server.git xserver
cd xserver

export ACLOCAL="aclocal -I /opt/X11/share/aclocal -I /usr/local/share/aclocal"
export PKG_CONFIG_PATH="/opt/X11/share/pkgconfig:/opt/X11/lib/pkgconfig"
export CFLAGS="-Wall -O0 -ggdb3 -arch i386 -arch x86_64 -pipe"
export OBJCFLAGS=$CFLAGS
export LDFLAGS=$CFLAGS

autoreconf -fvi
./configure --prefix=/opt/X11 --disable-dependency-tracking --enable-maintainer-mode --with-apple-application-name=XQuartz --with-bundle-id-prefix=org.xquartz --disable-xquartz --enable-xvfb --enable-xnest --enable-kdrive
make
sudo make install
