#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>

#define MATRIX_SIZE 1000  // Define a large size for the matrix
#define NUM_THREADS 8     // Define the number of threads

double **matrixA, **matrixB, **matrixC;

typedef struct {
    int startRow;
    int endRow;
} ThreadData;

void* multiplyMatrix(void* arg) {
    ThreadData* data = (ThreadData*) arg;
    int i, j, k;

    for (i = data->startRow; i < data->endRow; i++) {
        for (j = 0; j < MATRIX_SIZE; j++) {
            matrixC[i][j] = 0;
            for (k = 0; k < MATRIX_SIZE; k++) {
                matrixC[i][j] += matrixA[i][k] * matrixB[k][j];
            }
        }
    }

    pthread_exit(0);
}

void writeMatrixToFile(double** matrix, const char* filename) {
    FILE* file = fopen(filename, "w");
    for (int i = 0; i < MATRIX_SIZE; i++) {
        for (int j = 0; j < MATRIX_SIZE; j++) {
            fprintf(file, "%f ", matrix[i][j]);
        }
        fprintf(file, "\n");
    }
    fclose(file);
}

void readMatrixFromFile(double** matrix, const char* filename) {
    FILE* file = fopen(filename, "r");
    for (int i = 0; i < MATRIX_SIZE; i++) {
        for (int j = 0; j < MATRIX_SIZE; j++) {
            fscanf(file, "%lf", &matrix[i][j]);
        }
    }
    fclose(file);
}

int main() {
    pthread_t threads[NUM_THREADS];
    ThreadData threadData[NUM_THREADS];
    int i, j;

    // Allocate memory for matrices
    matrixA = (double**) malloc(MATRIX_SIZE * sizeof(double*));
    matrixB = (double**) malloc(MATRIX_SIZE * sizeof(double*));
    matrixC = (double**) malloc(MATRIX_SIZE * sizeof(double*));

    for (i = 0; i < MATRIX_SIZE; i++) {
        matrixA[i] = (double*) malloc(MATRIX_SIZE * sizeof(double));
        matrixB[i] = (double*) malloc(MATRIX_SIZE * sizeof(double));
        matrixC[i] = (double*) malloc(MATRIX_SIZE * sizeof(double));
    }

    // Initialize matrixA and matrixB with random values
    for (i = 0; i < MATRIX_SIZE; i++) {
        for (j = 0; j < MATRIX_SIZE; j++) {
            matrixA[i][j] = rand() % 100;
            matrixB[i][j] = rand() % 100;
        }
    }

    // Write matrixA to a file
    writeMatrixToFile(matrixA, "matrixA.txt");
    // Read matrixA back from the file (optional)
    readMatrixFromFile(matrixA, "matrixA.txt");

    // Multithreaded matrix multiplication
    int rowsPerThread = MATRIX_SIZE / NUM_THREADS;

    for (i = 0; i < NUM_THREADS; i++) {
        threadData[i].startRow = i * rowsPerThread;
        threadData[i].endRow = (i == NUM_THREADS - 1) ? MATRIX_SIZE : (i + 1) * rowsPerThread;
        pthread_create(&threads[i], NULL, multiplyMatrix, (void*) &threadData[i]);
    }

    // Wait for all threads to complete
    for (i = 0; i < NUM_THREADS; i++) {
        pthread_join(threads[i], NULL);
    }

    // Write the result matrix to a file
    writeMatrixToFile(matrixC, "matrixC.txt");

    // Free memory
    for (i = 0; i < MATRIX_SIZE; i++) {
        free(matrixA[i]);
        free(matrixB[i]);
        free(matrixC[i]);
    }
    free(matrixA);
    free(matrixB);
    free(matrixC);

    printf("Matrix multiplication completed and results saved to matrixC.txt\n");
    return 0;
}
