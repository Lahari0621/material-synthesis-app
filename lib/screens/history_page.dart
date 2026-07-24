import 'package:flutter/material.dart';

import '../models/user_model.dart';
import '../services/api_service.dart';

class HistoryPage extends StatefulWidget {
  final User user;

  const HistoryPage({required this.user});

  @override
  _HistoryPageState createState() => _HistoryPageState();
}

class _HistoryPageState extends State<HistoryPage> {
  List<Map<String, dynamic>> _experiments = [];
  bool _isLoading = true;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _loadHistory();
  }

  Future<void> _loadHistory() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    final result = await ApiService.fetchHistory(widget.user.id);
    if (!mounted) {
      return;
    }

    if (result.containsKey('error')) {
      setState(() {
        _experiments = [];
        _errorMessage =
            result['error']?.toString() ?? 'Failed to fetch history.';
        _isLoading = false;
      });
      return;
    }

    final rawList =
        result['history'] ?? result['records'] ?? result['data'] ?? [];
    final parsed = <Map<String, dynamic>>[];

    if (rawList is List) {
      for (final item in rawList) {
        if (item is! Map) {
          continue;
        }

        parsed.add({
          'id':
              item['id'] ?? item['experiment_id'] ?? item['prediction_id'] ?? 0,
          'baseMaterial':
              (item['base_material'] ?? item['baseMaterial'] ?? 'N/A')
                  .toString(),
          'targetMaterial':
              (item['target_material'] ?? item['targetMaterial'] ?? 'N/A')
                  .toString(),
          'temperature':
              (item['temperature'] ??
                      item['predicted_temperature'] ??
                      item['temperature_c'] ??
                      'N/A')
                  .toString(),
          'date':
              (item['created_at'] ?? item['date'] ?? item['timestamp'] ?? 'N/A')
                  .toString(),
          'status': (item['status'] ?? 'Success').toString(),
          'phase': (item['phase'] ?? item['target_phase'] ?? 'synthesis')
              .toString(),
        });
      }
    }

    setState(() {
      _experiments = parsed;
      _isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final isCompact = constraints.maxWidth < 700;
        final pagePadding = isCompact ? 16.0 : 32.0;

        return SingleChildScrollView(
          child: Padding(
            padding: EdgeInsets.all(pagePadding),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Synthesis History',
                  style: TextStyle(
                    fontSize: isCompact ? 28 : 36,
                    fontWeight: FontWeight.bold,
                    color: Colors.blueGrey[900],
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'View all your past synthesis experiments and predictions',
                  style: TextStyle(fontSize: 16, color: Colors.blueGrey[600]),
                ),
                const SizedBox(height: 32),

                LayoutBuilder(
                  builder: (context, constraints) {
                    final cards = [
                      _StatCard(
                        icon: Icons.check_circle,
                        title: 'Successful',
                        value: _experiments.length.toString(),
                        color: Colors.green[600]!,
                      ),
                      _StatCard(
                        icon: Icons.history,
                        title: 'Total Experiments',
                        value: _experiments.length.toString(),
                        color: Colors.blue[600]!,
                      ),
                      _StatCard(
                        icon: Icons.trending_up,
                        title: 'Success Rate',
                        value: _experiments.isEmpty ? '0%' : '100%',
                        color: Colors.orange[600]!,
                      ),
                    ];

                    if (constraints.maxWidth < 900) {
                      return Column(
                        children: [
                          for (final card in cards) ...[
                            card,
                            const SizedBox(height: 12),
                          ],
                        ],
                      );
                    }

                    return Row(
                      children: [
                        for (var i = 0; i < cards.length; i++) ...[
                          Expanded(child: cards[i]),
                          if (i < cards.length - 1) const SizedBox(width: 16),
                        ],
                      ],
                    );
                  },
                ),
                const SizedBox(height: 32),

                // Experiments List
                Card(
                  elevation: 8,
                  shadowColor: Colors.black12,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16),
                  ),
                  color: Colors.white,
                  child: Padding(
                    padding: EdgeInsets.all(isCompact ? 16.0 : 24.0),
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
                            Expanded(
                              child: Text(
                                'Experiment Records',
                                style: TextStyle(
                                  fontSize: isCompact ? 18 : 22,
                                  fontWeight: FontWeight.bold,
                                  color: Colors.blueGrey[900],
                                ),
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 24),
                        if (_isLoading)
                          const Padding(
                            padding: EdgeInsets.all(24.0),
                            child: Center(child: CircularProgressIndicator()),
                          )
                        else if (_errorMessage != null)
                          _HistoryMessage(
                            icon: Icons.cloud_off_outlined,
                            message: _errorMessage!,
                            actionLabel: 'Retry',
                            onAction: _loadHistory,
                          )
                        else if (_experiments.isEmpty)
                          _HistoryMessage(
                            icon: Icons.search_off,
                            message:
                                'No experiment history found for this user yet.',
                            actionLabel: 'Refresh',
                            onAction: _loadHistory,
                          )
                        else
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
      },
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
    return LayoutBuilder(
      builder: (context, constraints) {
        final isCompact = constraints.maxWidth < 760;

        final details = Column(
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
            Wrap(
              spacing: 12,
              runSpacing: 8,
              crossAxisAlignment: WrapCrossAlignment.center,
              children: [
                Row(
                  mainAxisSize: MainAxisSize.min,
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
                  ],
                ),
                Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      Icons.calendar_today,
                      size: 16,
                      color: Colors.blue[600],
                    ),
                    const SizedBox(width: 4),
                    Text(
                      experiment['date'],
                      style: TextStyle(fontSize: 13, color: Colors.grey[700]),
                    ),
                  ],
                ),
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
        );

        final button = ElevatedButton(
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
        );

        if (isCompact) {
          return Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [details, const SizedBox(height: 12), button],
          );
        }

        return Row(
          children: [
            Expanded(child: details),
            const SizedBox(width: 16),
            button,
          ],
        );
      },
    );
  }
}

class _HistoryMessage extends StatelessWidget {
  final IconData icon;
  final String message;
  final String actionLabel;
  final VoidCallback onAction;

  const _HistoryMessage({
    required this.icon,
    required this.message,
    required this.actionLabel,
    required this.onAction,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 24.0, horizontal: 8.0),
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 320),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(icon, size: 40, color: Colors.blueGrey[400]),
              const SizedBox(height: 12),
              Text(
                message,
                textAlign: TextAlign.center,
                style: TextStyle(
                  color: Colors.blueGrey[700],
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 12),
              TextButton(onPressed: onAction, child: Text(actionLabel)),
            ],
          ),
        ),
      ),
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
