import 'package:flutter/material.dart';
// Import the widget we just built!
import '../widgets/command_center_card.dart';
import '../services/api_service.dart';
import 'login_screen.dart';

class SynthesisDashboard extends StatefulWidget {
  final int userId;

  const SynthesisDashboard({this.userId = 1});

  @override
  _SynthesisDashboardState createState() => _SynthesisDashboardState();
}

class _SynthesisDashboardState extends State<SynthesisDashboard> {
  bool _isLoggingOut = false;

  Future<void> _handleLogout() async {
    setState(() {
      _isLoggingOut = true;
    });

    // Call the logout API
    await ApiService.logout(widget.userId);

    setState(() {
      _isLoggingOut = false;
    });

    // Navigate back to login screen regardless of the API response
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (context) => LoginScreen()),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor:
          Colors.grey[50], // Very light background to make the white card pop
      appBar: AppBar(
        title: const Text(
          "AI Synthesis Dashboard",
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        backgroundColor: Colors.lightBlue[800], // Professional sky-blue
        elevation: 0,
        actions: [
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16.0),
            child: Center(
              child: Text(
                'User ID: ${widget.userId}',
                style: const TextStyle(fontSize: 14, color: Colors.white),
              ),
            ),
          ),
          PopupMenuButton<String>(
            onSelected: (String value) {
              if (value == 'logout') {
                _handleLogout();
              }
            },
            itemBuilder: (BuildContext context) => <PopupMenuEntry<String>>[
              const PopupMenuItem<String>(
                value: 'logout',
                child: Row(
                  children: [
                    Icon(Icons.logout, color: Colors.redAccent),
                    SizedBox(width: 10),
                    Text('Logout'),
                  ],
                ),
              ),
            ],
            icon: _isLoggingOut
                ? const SizedBox(
                    width: 24,
                    height: 24,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                    ),
                  )
                : const Icon(Icons.menu),
          ),
          const SizedBox(width: 8),
        ],
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // This is where we place your new Command Center Card!
              CommandCenterCard(),

              const SizedBox(height: 24),

              // We will build the AI Telemetry Panel down here next!
            ],
          ),
        ),
      ),
    );
  }
}
