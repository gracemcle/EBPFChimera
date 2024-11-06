# Makefile for installing various packages on Alpine Linux

.PHONY: all clang llvm go bpftrace linux-headers tmux cargo bcc git base-cbuild

all: clang llvm go bpftrace linux-headers tmux cargo bcc git base-cbuild

clang:
	@echo "Installing clang..."
	apk add clang

llvm:
	@echo "Installing llvm..."
	apk add llvm

go:
	@echo "Installing go..."
	apk add go

bpftrace:
	@echo "Installing bpftrace..."
	apk add bpftrace

linux-headers:
	@echo "Installing linux-headers..."
	apk add linux-headers

tmux:
	@echo "Installing tmux..."
	apk add tmux

cargo:
	@echo "Installing cargo..."
	apk add cargo

bcc:
	@echo "Installing bcc..."
	apk add bcc

base-cbuild:
	@echo "Installing base-cbuild..."
	apk add base-cbuild
