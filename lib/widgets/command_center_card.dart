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
  Map<String, dynamic>? _feasibilityResult;

  final TextEditingController _baseMaterialController = TextEditingController();
  final TextEditingController _targetMaterialController =
      TextEditingController();
  final TextEditingController _targetPhaseController = TextEditingController();

  // --- THE NEW API LOGIC ---
  Future<void> _initiateSimulation() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
      _feasibilityResult = null;
    });

    final baseMat = _baseMaterialController.text.trim();
    final targetMat = _targetMaterialController.text.trim();

    if (baseMat.isEmpty || targetMat.isEmpty) {
      setState(() {
        _errorMessage = "Base and Target materials are required.";
        _isLoading = false;
      });
      return;
    }

    final result = await ApiService.predictSynthesis(
      baseMaterial: baseMat,
      targetMaterial: targetMat,
      targetPhase: _isPhaseSpecific
          ? _targetPhaseController.text.trim()
          : 'synthesis',
    );

    if (!mounted) {
      return;
    }

    setState(() {
      _isLoading = false;
    });

    if (result.containsKey('error')) {
      setState(() {
        _errorMessage = result['error'];
      });
      return;
    }

    final feasible = result['feasible'] == true;
    if (!feasible) {
      setState(() {
        _feasibilityResult = result;
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

  Widget _buildFeasibilityResultCard(Map<String, dynamic> result) {
    final message = result['message']?.toString().trim();
    final reason = result['reason']?.toString().trim();
    final recommendations = result['recommendations'];

    final recommendationItems = recommendations is List
        ? recommendations
              .where((item) => item != null)
              .map((item) => item.toString().trim())
              .where((item) => item.isNotEmpty)
              .toList()
        : recommendations is String && recommendations.trim().isNotEmpty
        ? recommendations
              .split(RegExp(r'\r?\n|;'))
              .map((item) => item.trim())
              .where((item) => item.isNotEmpty)
              .toList()
        : <String>[];

    Widget buildField(String label, String? value) {
      if (value == null || value.isEmpty) {
        return const SizedBox.shrink();
      }

      return Padding(
        padding: const EdgeInsets.only(top: 10),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              label,
              style: TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.bold,
                color: Colors.blueGrey[900],
              ),
            ),
            const SizedBox(height: 4),
            Text(
              value,
              style: TextStyle(fontSize: 14, color: Colors.blueGrey[700]),
            ),
          ],
        ),
      );
    }

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.amber[50],
        border: Border.all(color: Colors.amber[200]!),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.report_outlined, color: Colors.amber[800]),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  'Feasibility review',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Colors.blueGrey[900],
                  ),
                ),
              ),
            ],
          ),
          buildField('Message', message),
          buildField('Reason', reason),
          if (recommendationItems.isNotEmpty) ...[
            const SizedBox(height: 10),
            Text(
              'Recommendations',
              style: TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.bold,
                color: Colors.blueGrey[900],
              ),
            ),
            const SizedBox(height: 6),
            for (final recommendation in recommendationItems)
              Padding(
                padding: const EdgeInsets.only(bottom: 4),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('- ', style: TextStyle(color: Colors.blueGrey[700])),
                    Expanded(
                      child: Text(
                        recommendation,
                        style: TextStyle(
                          fontSize: 14,
                          color: Colors.blueGrey[700],
                        ),
                      ),
                    ),
                  ],
                ),
              ),
          ],
        ],
      ),
    );
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

            if (_feasibilityResult != null) ...[
              _buildFeasibilityResultCard(_feasibilityResult!),
              const SizedBox(height: 16),
            ],

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
                      "CHECK FEASIBILITY",
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
