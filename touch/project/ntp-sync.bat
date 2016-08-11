echo "current sync to host:"
w32tm /stripchart /computer:131.179.142.99 /samples:5 /dataonly

echo "syncing to host..."
w32tm /config /manualpeerlist:131.179.142.99 /syncfromflags:manual /update

echo "current sync to host:"
w32tm /stripchart /computer:131.179.142.99 /samples:5 /dataonly