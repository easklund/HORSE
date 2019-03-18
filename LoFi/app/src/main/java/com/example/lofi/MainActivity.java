package com.example.lofi;

import android.app.AlertDialog;
import android.content.Context;
import android.content.DialogInterface;
import android.content.SharedPreferences;
import android.media.MediaPlayer;
import android.os.AsyncTask;
import android.support.v4.content.ContextCompat;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;

public class MainActivity extends AppCompatActivity {
    private TcpClient mTcpClient;
    private boolean connectionRunning = false;
    private SharedPreferences sharedPref;
    private String serverAddress;
    private int serverPort = 5005;
    private boolean backWrongPosition = false;
    private boolean footWrongPosition = false;
    private boolean isBackReferenceSet = false;
    private boolean isFootReferenceSet = false;
    private float currentBackAngle = 0;
    private float currentFootAngle = 0;
    private float referenceBackAngle = 0;
    private float referenceFootAngle = 0;
    private boolean backIndicated = false;
    private boolean footIndicated = false;
    private static final float BACK_SENSITIVITY = 20;
    private static final float FOOT_SENSITIVITY = 30;
    private MediaPlayer backSound;
    private MediaPlayer footSound;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        sharedPref = this.getPreferences(Context.MODE_PRIVATE);
        setContentView(R.layout.activity_main);
        serverAddress = sharedPref.getString("server_address", "192.168.0.40");
        ((TextView) findViewById(R.id.txtIP)).setText(serverAddress);
        (findViewById(R.id.txtBackWrongPosition)).setVisibility(View.INVISIBLE);
        (findViewById(R.id.txtFootWrongPosition)).setVisibility(View.INVISIBLE);
        (findViewById(R.id.btnSetBackReference)).setEnabled(false);
        (findViewById(R.id.btnSetFootReference)).setEnabled(false);

        backSound = MediaPlayer.create(this, R.raw.back);
        footSound = MediaPlayer.create(this, R.raw.feet);
    }


    public void onClickConnect(View view) {
        if (!connectionRunning) {
            ((TextView) findViewById(R.id.txtDisplay)).setText("Connecting...");
            connectionRunning = true;
            Log.e("TCP", "Connecting...");
            new ConnectTask().execute("");
            ((Button) findViewById(R.id.btnChangeIP)).setEnabled(false);
        } else {
            connectionRunning = false;
            Log.e("TCP", "Disconnecting...");
            new DisconnectTask().execute();
        }
    }

    public void onChangeIP(View view) {
        final EditText txtEnterIP = new EditText(this);
        txtEnterIP.setHint(serverAddress);

        new AlertDialog.Builder(this)
                .setTitle("Change IP")
                .setView(txtEnterIP)
                .setPositiveButton("Change", new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int whichButton) {
                        serverAddress = txtEnterIP.getText().toString().trim();
                        ((TextView) findViewById(R.id.txtIP)).setText(serverAddress);
                        SharedPreferences.Editor editor = sharedPref.edit();
                        editor.putString("server_address", serverAddress);
                        editor.commit();
                    }
                })
                .setNegativeButton("Cancel", new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int whichButton) {
                    }
                })
                .show();
    }

    public void onSetBackReference(View view) {
        this.referenceBackAngle = this.currentBackAngle;
        isBackReferenceSet = true;
        ((TextView) findViewById(R.id.txtBackReference)).setText("Back reference is " + this.referenceBackAngle);
    }

    public void onSetFootReference(View view) {
        this.referenceFootAngle = this.currentFootAngle;
        isFootReferenceSet = true;
        ((TextView) findViewById(R.id.txtFootReference)).setText("Foot reference is " + this.referenceFootAngle);
    }

    private void displayIncorrectPosition() {
        if (backWrongPosition || footWrongPosition) {
            findViewById(R.id.layout).setBackgroundColor(ContextCompat.getColor(this, R.color.slouchingBackground));
        } else {
            findViewById(R.id.layout).setBackgroundColor(ContextCompat.getColor(this, android.R.color.background_light));
        }
        if (backWrongPosition) {
            (findViewById(R.id.txtBackWrongPosition)).setVisibility(View.VISIBLE);
            if (!backIndicated) {
                backSound.start();
                backIndicated = true;
            }
        } else {
            (findViewById(R.id.txtBackWrongPosition)).setVisibility(View.INVISIBLE);
            backIndicated = false;
        }
        if (footWrongPosition) {
            (findViewById(R.id.txtFootWrongPosition)).setVisibility(View.VISIBLE);
            if (!footIndicated) {
                footSound.start();
                footIndicated = true;
            }
        } else {
            (findViewById(R.id.txtFootWrongPosition)).setVisibility(View.INVISIBLE);
            footIndicated = false;
        }

    }

    public class ConnectTask extends AsyncTask<String, String, TcpClient> {

        @Override
        protected TcpClient doInBackground(String... message) {
            // Update button and textview
            Log.e("TCP", "ConnectTask running...");
            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    Button btnConnect = findViewById(R.id.btnConnect);
                    Button setBackReference = findViewById(R.id.btnSetBackReference);
                    Button setFootReference = findViewById(R.id.btnSetFootReference);
                    TextView txtDisplay = findViewById(R.id.txtDisplay);

                    btnConnect.setText("Disconnect");
                    setBackReference.setEnabled(true);
                    setFootReference.setEnabled(true);
                    txtDisplay.setText("Connecting...");
                }
            });

            //we create a TCPClient object and
            mTcpClient = new TcpClient(serverAddress, serverPort, new TcpClient.OnMessageReceived() {
                @Override
                //here the messageReceived method is implemented
                public void messageReceived(String message) {
                    //this method calls the onProgressUpdate
                    publishProgress(message);
                }
            });
            mTcpClient.run();

            return null;
        }

        @Override
        protected void onProgressUpdate(String... values) {
            super.onProgressUpdate(values);

            TextView display = findViewById(R.id.txtDisplay);
            String inputs[] = values[0].split(", ");
            display.setText(inputs[0] + ", " + inputs[1]);

            float newBackAngle = Float.parseFloat(inputs[0]);
            float newFootAngle = Float.parseFloat(inputs[1]);
            currentBackAngle = newBackAngle;
            currentFootAngle = newFootAngle;

            if (isBackReferenceSet)
                backWrongPosition = (newBackAngle - referenceBackAngle >= BACK_SENSITIVITY);
            if (isFootReferenceSet)
                footWrongPosition = (newFootAngle - referenceFootAngle >= FOOT_SENSITIVITY);

            displayIncorrectPosition();

            //in the arrayList we add the messaged received from server
//            arrayList.add(values[0]);
            // notify the adapter that the data set has changed. This means that new message received
            // from server was added to the list
//            mAdapter.notifyDataSetChanged();
        }
    }

    /**
     * Disconnects using a background task to avoid doing long/network operations on the UI thread
     */
    public class DisconnectTask extends AsyncTask<Void, Void, Void> {
//        @Override
//        protected void onPreExecute() {
//            super.onPreExecute();
//            Log.e("TCP", "onPreExecute");
//        }

        @Override
        protected Void doInBackground(Void... voids) {
            Log.e("TCP", "DisconnectTask running...");
            // disconnect
            mTcpClient.stopClient();
            mTcpClient = null;

            return null;
        }

        @Override
        protected void onPostExecute(Void nothing) {
            super.onPostExecute(nothing);
//            ((TextView) findViewById(R.id.txtDisplay)).setText("Press connect");
//            ((Button) findViewById(R.id.btnConnect)).setText("Connect");
        }
    }
}
