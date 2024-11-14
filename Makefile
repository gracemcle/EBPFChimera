
# Compiler and flags
CC = clang
CFLAGS = -O2 -Wall -Wextra -pthread
MUSL_LIB = /path/to/musl/lib
MUSL_INCLUDE = /path/to/musl/include
LDFLAGS = -L$(MUSL_LIB) -static

# Source files
SRC = matrix_mult.c
OBJ = $(SRC:.c=.o)
EXEC = matrix_mult

# Build rules
all: $(EXEC)

# Compile the program
$(EXEC): $(OBJ)
	$(CC) $(LDFLAGS) -o $(EXEC) $(OBJ) -I$(MUSL_INCLUDE) -L$(MUSL_LIB) -pthread

# Compile source files into object files
%.o: %.c
	$(CC) $(CFLAGS) -I$(MUSL_INCLUDE) -c $< -o $@

# Clean up generated files
clean:
	rm -f $(OBJ) $(EXEC)

.PHONY: all clean
