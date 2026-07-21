import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../screens/telemetry_screen.dart'; // Import our new screen

class CommandCenterCard extends StatefulWidget {
  @override
  _CommandCenterCardState createState() => _CommandCenterCardState();
}

class _CommandCenterCardState extends State<CommandCenterCard> {
  bool _isPhaseSpecific = false;
  bool _isLoading = false;
  String? _errorMessage;

  final TextEditingController _baseMaterialController = TextEditingController();
  final TextEditingController _targetMaterialController =
      TextEditingController();
  final TextEditingController _targetPhaseController = TextEditingController();

  // --- THE NEW API LOGIC ---
  Future<void> _initiateSimulation() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    final baseMat = _baseMaterialController.text.trim();
    final targetMat = _targetMaterialController.text.trim();
    // Only grab the phase if the toggle is active
    final phase = _isPhaseSpecific
        ? _targetPhaseController.text.trim()
        : 'synthesis';

    if (baseMat.isEmpty || targetMat.isEmpty) {
      setState(() {
        _errorMessage = "Base and Target materials are required.";
        _isLoading = false;
      });
      return;
    }

    // Call the Python AI!
    final result = await ApiService.predictSynthesis(baseMat, targetMat, phase);

    setState(() {
      _isLoading = false;
    });

    if (result.containsKey('error')) {
      setState(() {
        _errorMessage = result['error'];
      });
    } else {
      // SUCCESS! Send the scientist to the Telemetry Screen with the AI data
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (context) => TelemetryScreen(aiData: result),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 8,
      shadowColor: Colors.black12,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      color: Colors.white,
      child: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              "Synthesis Parameters",
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
                color: Colors.blueGrey[900],
              ),
            ),
            const SizedBox(height: 24),

            // --- THE TOGGLE ---
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                FilterChip(
                  label: const Text("Standard Synthesis"),
                  selected: !_isPhaseSpecific,
                  selectedColor: Colors.lightBlue[100],
                  checkmarkColor: Colors.lightBlue[800],
                  onSelected: (bool selected) {
                    setState(() => _isPhaseSpecific = false);
                  },
                ),
                const SizedBox(width: 16),
                FilterChip(
                  label: const Text("Advanced Phase Target"),
                  selected: _isPhaseSpecific,
                  selectedColor: Colors.lightBlue[100],
                  checkmarkColor: Colors.lightBlue[800],
                  onSelected: (bool selected) {
                    setState(() => _isPhaseSpecific = true);
                  },
                ),
              ],
            ),
            const SizedBox(height: 24),

            // --- ALWAYS VISIBLE INPUTS ---
            TextFormField(
              controller: _baseMaterialController,
              decoration: const InputDecoration(
                labelText: "Base Material (e.g., Zinc)",
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.science_outlined),
              ),
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _targetMaterialController,
              decoration: const InputDecoration(
                labelText: "Target Material (e.g., Zinc)",
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.transform),
              ),
            ),
            const SizedBox(height: 16),

            // --- CONDITIONALLY RENDERED INPUT ---
            if (_isPhaseSpecific) ...[
              TextFormField(
                controller: _targetPhaseController,
                decoration: const InputDecoration(
                  labelText: "Target Phase (e.g., Hexagonal)",
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.hub_outlined),
                ),
              ),
              const SizedBox(height: 24),
            ],

            // --- ERROR MESSAGE ---
            if (_errorMessage != null)
              Padding(
                padding: const EdgeInsets.only(bottom: 16.0),
                child: Text(
                  _errorMessage!,
                  style: const TextStyle(
                    color: Colors.redAccent,
                    fontWeight: FontWeight.bold,
                  ),
                  textAlign: TextAlign.center,
                ),
              ),

            // --- THE INITIATE BUTTON OR LOADING SPINNER ---
            _isLoading
                ? const Center(child: CircularProgressIndicator())
                : ElevatedButton(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.orange[600],
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                    ),
                    onPressed:
                        _initiateSimulation, // Connect to our new function!
                    child: const Text(
                      "INITIATE AI SIMULATION",
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ),
                  ),
          ],
        ),
      ),
    );
  }
}
