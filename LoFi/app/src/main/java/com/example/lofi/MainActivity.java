package com.example.lofi;

import android.app.AlertDialog;
import android.content.DialogInterface;
import android.os.AsyncTask;
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
    private String serverAddress = "192.168.0.40";
    private int serverPort = 5005;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        ((TextView) findViewById(R.id.txtIP)).setText(serverAddress);
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
                        serverAddress = txtEnterIP.getText().toString();
                        ((TextView) findViewById(R.id.txtIP)).setText(serverAddress);
                    }
                })
                .setNegativeButton("Cancel", new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int whichButton) {
                    }
                })
                .show();
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
                    TextView txtDisplay = findViewById(R.id.txtDisplay);

                    btnConnect.setText("Disconnect");
                    txtDisplay.setText("Connecting...");
                }
            });

            //we create a TCPClient object and
            mTcpClient = new TcpClient(serverAddress, serverPort, new TcpClient.OnMessageReceived() {
                @Override
                //here the messageReceived method is implemented
                public void messageReceived(String message) {
                    Log.e("TCP", "Got some message");
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

            TextView display = (TextView) findViewById(R.id.txtDisplay);
            display.setText(values[0]);
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
        @Override
        protected void onPreExecute() {
            super.onPreExecute();
            Log.e("TCP", "onPreExecure");
        }

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
