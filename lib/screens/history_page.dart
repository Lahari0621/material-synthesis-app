import 'package:flutter/material.dart';

class HistoryPage extends StatefulWidget {
  @override
  _HistoryPageState createState() => _HistoryPageState();
}

class _HistoryPageState extends State<HistoryPage> {
  // Mock data for demonstration
  final List<Map<String, dynamic>> _experiments = [
    {
      'id': 1,
      'baseMaterial': 'Iron Oxide (Fe2O3)',
      'targetMaterial': 'Iron Nanoparticles',
      'temperature': '766.5°C',
      'date': '2024-05-25',
      'status': 'Success',
      'phase': 'synthesis',
    },
    {
      'id': 2,
      'baseMaterial': 'Copper Sulfate',
      'targetMaterial': 'Copper Oxide',
      'temperature': '850.0°C',
      'date': '2024-05-24',
      'status': 'Success',
      'phase': 'crystalline',
    },
    {
      'id': 3,
      'baseMaterial': 'Titanium Dioxide',
      'targetMaterial': 'Titanium Nanoparticles',
      'temperature': '920.0°C',
      'date': '2024-05-23',
      'status': 'Success',
      'phase': 'synthesis',
    },
    {
      'id': 4,
      'baseMaterial': 'Zinc Oxide',
      'targetMaterial': 'Zinc Sulfide',
      'temperature': '750.0°C',
      'date': '2024-05-22',
      'status': 'Success',
      'phase': 'synthesis',
    },
    {
      'id': 5,
      'baseMaterial': 'Nickel Chloride',
      'targetMaterial': 'Nickel Nanoparticles',
      'temperature': '680.0°C',
      'date': '2024-05-21',
      'status': 'Success',
      'phase': 'synthesis',
    },
  ];

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      child: Padding(
        padding: const EdgeInsets.all(32.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Synthesis History',
              style: TextStyle(
                fontSize: 36,
                fontWeight: FontWeight.bold,
                color: Colors.blueGrey[900],
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'View all your past synthesis experiments and predictions',
              style: TextStyle(fontSize: 16, color: Colors.blueGrey[600]),
            ),
            const SizedBox(height: 48),

            // Summary Stats
            Row(
              children: [
                Expanded(
                  child: _StatCard(
                    icon: Icons.check_circle,
                    title: 'Successful',
                    value: _experiments.length.toString(),
                    color: Colors.green[600]!,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: _StatCard(
                    icon: Icons.history,
                    title: 'Total Experiments',
                    value: _experiments.length.toString(),
                    color: Colors.blue[600]!,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: _StatCard(
                    icon: Icons.trending_up,
                    title: 'Success Rate',
                    value: '100%',
                    color: Colors.orange[600]!,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 48),

            // Experiments List
            Card(
              elevation: 8,
              shadowColor: Colors.black12,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16),
              ),
              color: Colors.white,
              child: Padding(
                padding: const EdgeInsets.all(24.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(
                          Icons.list,
                          size: 28,
                          color: Colors.lightBlue[800],
                        ),
                        const SizedBox(width: 12),
                        Text(
                          'Experiment Records',
                          style: TextStyle(
                            fontSize: 22,
                            fontWeight: FontWeight.bold,
                            color: Colors.blueGrey[900],
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 24),
                    ListView.separated(
                      shrinkWrap: true,
                      physics: const NeverScrollableScrollPhysics(),
                      itemCount: _experiments.length,
                      separatorBuilder: (context, index) =>
                          Divider(color: Colors.grey[300], height: 32),
                      itemBuilder: (context, index) {
                        final experiment = _experiments[index];
                        return _ExperimentCard(
                          experiment: experiment,
                          onView: () {
                            _showExperimentDetails(context, experiment);
                          },
                        );
                      },
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 48),
          ],
        ),
      ),
    );
  }

  void _showExperimentDetails(
    BuildContext context,
    Map<String, dynamic> experiment,
  ) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Experiment #${experiment['id']}'),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _DetailRow('Base Material:', experiment['baseMaterial']),
              const SizedBox(height: 12),
              _DetailRow('Target Material:', experiment['targetMaterial']),
              const SizedBox(height: 12),
              _DetailRow('Phase:', experiment['phase']),
              const SizedBox(height: 12),
              _DetailRow('Temperature:', experiment['temperature']),
              const SizedBox(height: 12),
              _DetailRow('Date:', experiment['date']),
              const SizedBox(height: 12),
              _DetailRow('Status:', experiment['status']),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }
}

class _StatCard extends StatelessWidget {
  final IconData icon;
  final String title;
  final String value;
  final Color color;

  const _StatCard({
    required this.icon,
    required this.title,
    required this.value,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 6,
      shadowColor: Colors.black12,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      color: Colors.white,
      child: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            Icon(icon, size: 36, color: color),
            const SizedBox(height: 12),
            Text(
              title,
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey[600],
                fontWeight: FontWeight.w500,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              value,
              style: TextStyle(
                fontSize: 28,
                fontWeight: FontWeight.bold,
                color: Colors.blueGrey[900],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _ExperimentCard extends StatelessWidget {
  final Map<String, dynamic> experiment;
  final VoidCallback onView;

  const _ExperimentCard({required this.experiment, required this.onView});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 8,
                      vertical: 4,
                    ),
                    decoration: BoxDecoration(
                      color: Colors.orange[100],
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: Text(
                      '#${experiment['id']}',
                      style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                        color: Colors.orange[600],
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      '${experiment['baseMaterial']} → ${experiment['targetMaterial']}',
                      style: TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.bold,
                        color: Colors.blueGrey[900],
                      ),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Row(
                children: [
                  Icon(Icons.thermostat, size: 16, color: Colors.red[600]),
                  const SizedBox(width: 4),
                  Text(
                    experiment['temperature'],
                    style: TextStyle(
                      fontSize: 13,
                      color: Colors.grey[700],
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  const SizedBox(width: 16),
                  Icon(Icons.calendar_today, size: 16, color: Colors.blue[600]),
                  const SizedBox(width: 4),
                  Text(
                    experiment['date'],
                    style: TextStyle(fontSize: 13, color: Colors.grey[700]),
                  ),
                  const SizedBox(width: 16),
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 8,
                      vertical: 4,
                    ),
                    decoration: BoxDecoration(
                      color: Colors.green[50],
                      border: Border.all(color: Colors.green[300]!),
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: Text(
                      experiment['status'],
                      style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                        color: Colors.green[600],
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(width: 16),
        ElevatedButton(
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.lightBlue[800],
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(6),
            ),
          ),
          onPressed: onView,
          child: const Text(
            'View Details',
            style: TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
              fontSize: 12,
            ),
          ),
        ),
      ],
    );
  }
}

class _DetailRow extends StatelessWidget {
  final String label;
  final String value;

  const _DetailRow(this.label, this.value);

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Text(
          label,
          style: TextStyle(
            fontWeight: FontWeight.bold,
            color: Colors.blueGrey[800],
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: Text(value, style: TextStyle(color: Colors.grey[700])),
        ),
      ],
    );
  }
}
