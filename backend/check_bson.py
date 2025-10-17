import sys, pkgutil
print(sys.executable)
print(sys.version)
print('bson available:', pkgutil.find_loader('bson') is not None)
