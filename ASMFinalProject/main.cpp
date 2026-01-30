#include <iostream>
#include <vector>
#include <iomanip>
#include <cstdio>

using namespace std;

extern "C" {
    // Calculate Average, Min, Max
    // arr: pointer to double array
    // count: number of elements
    // avg, min, max: pointers to store results
    void CalcStats(double* arr, int count, double* avg, double* min, double* max);

    // Convert Celsius to Fahrenheit
    double CelsiusToFahrenheit(double c);

    // Convert Fahrenheit to Celsius
    double FahrenheitToCelsius(double f);
    
    // Calculate Standard Deviation
    double CalculateStandardDeviation(double* arr, int count, double avg);

    // Increase Brightness using MMX
    void MmxIncreaseBrightness(unsigned char* data, int n, unsigned char amount);
}

int main() {
    // 1. Use double array to store N temperature data (e.g., 10-30)
    const int N = 10;
    double temperatures[N] = { 25.5, 26.0, 24.8, 27.2, 23.5, 28.0, 25.1, 26.5, 24.0, 25.8 };

    cout << "Temperature Data (Celsius): ";
    for (int i = 0; i < N; ++i) {
        cout << temperatures[i] << " ";
    }
    cout << endl << endl;

    // 2. Call assembly functions to calculate Avg, Min, Max
    double avg = 0.0;
    double min = 0.0;
    double max = 0.0;

    CalcStats(temperatures, N, &avg, &min, &max);

    cout << fixed << setprecision(2);
    cout << "Statistics (calculated by ASM):" << endl;
    cout << "Average: " << avg << " C" << endl;
    cout << "Minimum: " << min << " C" << endl;
    cout << "Maximum: " << max << " C" << endl;
    cout << endl;

    // 3. Optional: Standard Deviation
    double stdDev = CalculateStandardDeviation(temperatures, N, avg);
    cout << "Standard Deviation: " << stdDev << endl;
    cout << endl;

    // 4. Temperature Conversion
    cout << "Conversions:" << endl;
    double testC = 100.0;
    double testF = CelsiusToFahrenheit(testC);
    cout << testC << " C = " << testF << " F" << endl;

    double testF2 = 32.0;
    double testC2 = FahrenheitToCelsius(testF2);
    cout << testF2 << " F = " << testC2 << " C" << endl;

    // 5. Image Brightness (MMX)
    unsigned char pixels[16] = { 
        10, 50, 100, 150, 200, 230, 240, 250, 
        5, 30, 80, 120, 180, 210, 220, 255 
    }; 
    int nPixels = 16; 
    unsigned char amount = 20;   // brightness increase 
 
    printf("\nPixels before: "); 
    for (int i = 0; i < nPixels; ++i) { 
        printf("%3u ", pixels[i]); 
    } 
    printf("\n"); 
 
    MmxIncreaseBrightness(pixels, nPixels, amount); 
 
    printf("Pixels after : "); 
    for (int i = 0; i < nPixels; ++i) { 
        printf("%3u ", pixels[i]); 
    } 
    printf("\n"); 

    return 0;
}
