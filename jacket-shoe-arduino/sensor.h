#ifndef SENSOR_H
#define SENSOR_H

struct sensor {
  int digitalPin;
  int address;
  int gyro_x, gyro_y, gyro_z;
  long gyro_x_cal, gyro_y_cal, gyro_z_cal;
  boolean set_gyro_angles;

  long acc_x, acc_y, acc_z, acc_total_vector;
  float angle_roll_acc, angle_pitch_acc;

  float angle_pitch, angle_roll;
  int angle_pitch_buffer, angle_roll_buffer;
  float angle_pitch_output, angle_roll_output;  
};

typedef struct sensor Sensor;

#endif /** SENSOR_H */
