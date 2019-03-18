///////////////////////////////////////////////////////////////////////////////////////
//THIS IS A DEMO SOFTWARE JUST FOR EXPERIMENT PURPOER IN A NONCOMERTIAL ACTIVITY
//Version: 1.0 (AUG, 2016)

//Gyro - Arduino UNO R3
//VCC  -  5V
//GND  -  GND
//SDA  -  A4
//SCL  -  A5
//INT  - port-2
//Jacket AD0 - D4
//Shoe   AD0 - D5

#include <Wire.h>
#include "sensor.h"
//Declaring some global variables

long loop_timer;
const int N_SENSORS = 2;
Sensor sensors[N_SENSORS];

void setup() {
  Sensor jacketSensor;
  Sensor shoeSensor;
  jacketSensor.digitalPin = 4;
  jacketSensor.address = 0x68;
  shoeSensor.digitalPin = 5;
  shoeSensor.address = 0x69;
  sensors[0] = jacketSensor;
  sensors[1] = shoeSensor;
  pinMode(4, OUTPUT);
  pinMode(5, OUTPUT);

  // Set AD0 to be high now, and later to low when we want to talk to it
  for (int i = 0; i < N_SENSORS; i++) {
    digitalWrite(shoeSensor.digitalPin, HIGH);
    sensors[i].gyro_x = 0;
    sensors[i].gyro_y = 0;
    sensors[i].gyro_z = 0;
    
    sensors[i].gyro_x_cal = 0;
    sensors[i].gyro_y_cal = 0;
    sensors[i].gyro_z_cal = 0;
    
    sensors[i].set_gyro_angles = false;
  
    sensors[i].acc_x = 0;
    sensors[i].acc_y = 0;
    sensors[i].acc_z = 0;
    sensors[i].acc_total_vector = 0;
    
    sensors[i].angle_roll_acc = 0;
    sensors[i].angle_pitch_acc = 0;
  
    sensors[i].angle_pitch = 0;
    sensors[i].angle_roll = 0;
    sensors[i].angle_pitch_buffer = 0;
    sensors[i].angle_roll_buffer = 0;
    sensors[i].angle_pitch_output = 0;
    sensors[i].angle_roll_output = 0;
  }
  
  Serial.begin(115200);
  pinMode(LED_BUILTIN, OUTPUT);                                        // To indicate calibration
  Serial.println("//calibrating");
  Wire.begin();                                                        //Start I2C as master

  for (int i = 0; i < N_SENSORS; i++) {
    setup_mpu_6050_registers(sensors[i]);                         //Setup the registers of the MPU-6050 
  }                            
  for (int cal_int = 0; cal_int < 1000 ; cal_int ++) {                  //Read the raw acc and gyro data from the MPU-6050 for 1000 times
    for (int i = 0; i < N_SENSORS; i++) {
      read_mpu_6050_data(&sensors[i]);
      sensors[i].gyro_x_cal += sensors[i].gyro_x;                                              //Add the gyro x offset to the gyro_x_cal variable
      sensors[i].gyro_y_cal += sensors[i].gyro_y;                                              //Add the gyro y offset to the gyro_y_cal variable
      sensors[i].gyro_z_cal += sensors[i].gyro_z;                                              //Add the gyro z offset to the gyro_z_cal variable
    }
    delay(3);                                                          //Delay 3us to have 250Hz for-loop
  }

  for (int i = 0; i < N_SENSORS; i++) {
    setup_mpu_6050_registers(sensors[i]);                         //Setup the registers of the MPU-6050
    
    // divide by 1000 to get avarage offset
    sensors[i].gyro_x_cal /= 1000;
    sensors[i].gyro_y_cal /= 1000;
    sensors[i].gyro_z_cal /= 1000;
  }    

  Serial.println("//calibrated");
  digitalWrite(LED_BUILTIN, HIGH);
  loop_timer = micros();                                               //Reset the loop timer
}

void loop(){
  for (int i = 0; i < N_SENSORS; i++) {
    read_mpu_6050_data(&sensors[i]);
  }
  
  for (int i = 0; i < N_SENSORS; i++) {    
    //Subtract the offset values from the raw gyro values
    sensors[i].gyro_x -= sensors[i].gyro_x_cal;
    sensors[i].gyro_y -= sensors[i].gyro_y_cal;
    sensors[i].gyro_z -= sensors[i].gyro_z_cal;

    //Gyro angle calculations . Note 0.0000763 = 1 / (200Hz x 65.5)
    sensors[i].angle_pitch += sensors[i].gyro_x * 0.0000763;                                   //Calculate the traveled pitch angle and add this to the angle_pitch variable
    sensors[i].angle_roll += sensors[i].gyro_y * 0.0000763;                                    //Calculate the traveled roll angle and add this to the angle_roll variable
    //0.000001332 = 0.0000763 * (3.142(PI) / 180degr) The Arduino sin function is in radians
    sensors[i].angle_pitch += sensors[i].angle_roll * sin(sensors[i].gyro_z * 0.000001332);               //If the IMU has yawed transfer the roll angle to the pitch angel
    sensors[i].angle_roll -= sensors[i].angle_pitch * sin(sensors[i].gyro_z * 0.000001332);               //If the IMU has yawed transfer the pitch angle to the roll angel
  
    //Accelerometer angle calculations
    sensors[i].acc_total_vector = sqrt((sensors[i].acc_x*sensors[i].acc_x)+(sensors[i].acc_y*sensors[i].acc_y)+(sensors[i].acc_z*sensors[i].acc_z));  //Calculate the total accelerometer vector
    //57.296 = 1 / (3.142 / 180) The Arduino asin function is in radians
    sensors[i].angle_pitch_acc = asin((float)sensors[i].acc_y/sensors[i].acc_total_vector)* 57.296;       //Calculate the pitch angle
    sensors[i].angle_roll_acc = asin((float)sensors[i].acc_x/sensors[i].acc_total_vector)* -57.296;       //Calculate the roll angle
    
    sensors[i].angle_pitch_acc -= 0.0;                                              //Accelerometer calibration value for pitch
    sensors[i].angle_roll_acc -= 0.0;                                               //Accelerometer calibration value for roll
  
    if(sensors[i].set_gyro_angles){                                                 //If the IMU is already started
      sensors[i].angle_pitch = sensors[i].angle_pitch * 0.9996 + sensors[i].angle_pitch_acc * 0.0004;     //Correct the drift of the gyro pitch angle with the accelerometer pitch angle
      sensors[i].angle_roll = sensors[i].angle_roll * 0.9996 + sensors[i].angle_roll_acc * 0.0004;        //Correct the drift of the gyro roll angle with the accelerometer roll angle
    }
    else{                                                                //At first start
      sensors[i].angle_pitch = sensors[i].angle_pitch_acc;                                     //Set the gyro pitch angle equal to the accelerometer pitch angle
      sensors[i].angle_roll = sensors[i].angle_roll_acc;                                       //Set the gyro roll angle equal to the accelerometer roll angle
      sensors[i].set_gyro_angles = true;                                            //Set the IMU started flag
    }
  
    //To dampen the pitch and roll angles a complementary filter is used
    sensors[i].angle_pitch_output = sensors[i].angle_pitch_output * 0.9 + sensors[i].angle_pitch * 0.1;   //Take 90% of the output pitch value and add 10% of the raw pitch value
    sensors[i].angle_roll_output = sensors[i].angle_roll_output * 0.9 + sensors[i].angle_roll * 0.1;      //Take 90% of the output roll value and add 10% of the raw roll value
  }
//  Serial.print(", ");
//  Serial.println(sensors[1].angle_pitch_output);
  
  while(micros() - loop_timer < 5000);                                 //Wait until the loop_timer reaches 5000us (200Hz) before starting the next loop
  Serial.println(String(sensors[0].angle_pitch_acc) + ", " + String(sensors[1].angle_pitch_acc));
  loop_timer = micros();//Reset the loop timer
}




void setup_mpu_6050_registers(Sensor sensor){
  //Activate the MPU-6050
  Wire.beginTransmission(sensor.address);                                        //Start communicating with the MPU-6050
  Wire.write(0x6B);                                                    //Send the requested starting register
  Wire.write(0x00);                                                    //Set the requested starting register
  Wire.endTransmission();
  //Configure the accelerometer (+/-8g)
  Wire.beginTransmission(sensor.address);                                        //Start communicating with the MPU-6050
  Wire.write(0x1C);                                                    //Send the requested starting register
  Wire.write(0x10);                                                    //Set the requested starting register
  Wire.endTransmission();
  //Configure the gyro (500dps full scale)
  Wire.beginTransmission(sensor.address);                                        //Start communicating with the MPU-6050
  Wire.write(0x1B);                                                    //Send the requested starting register
  Wire.write(0x08);                                                    //Set the requested starting register
  Wire.endTransmission();
}


void read_mpu_6050_data(Sensor *sensor){                                //Subroutine for reading the raw gyro and accelerometer data
  Wire.beginTransmission(sensor->address);                                        //Start communicating with the MPU-6050
  Wire.write(0x3B);                                                    //Send the requested starting register
  Wire.endTransmission();                                              //End the transmission
  Wire.requestFrom(sensor->address,14);                                           //Request 14 bytes from the MPU-6050
  while(Wire.available() < 14);                                        //Wait until all the bytes are received
  sensor->acc_x = Wire.read()<<8|Wire.read();
  sensor->acc_y = Wire.read()<<8|Wire.read();
  sensor->acc_z = Wire.read()<<8|Wire.read();
//  temp = Wire.read()<<8|Wire.read();
  sensor->gyro_x = Wire.read()<<8|Wire.read();
  sensor->gyro_y = Wire.read()<<8|Wire.read();
  sensor->gyro_z = Wire.read()<<8|Wire.read();
}
