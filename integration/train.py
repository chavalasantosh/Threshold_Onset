"""
Training loop for Constraint-First LLM (SFLM)
Runs multiple epochs to observe learning over time.

Expected observations:
- avg_bias increases
- max_bias separates
- dominant paths stabilize
- output length increases
- repetition decreases naturally
"""

import sys
from pathlib import Path

# Add integration directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "integration"))

from integration.preference_learner import PreferenceLearner


def run_training(epochs=200, print_interval=10, verbose=False):
    """
    Run training loop with persistent learner across epochs.

    Args:
        epochs: Number of training epochs
        print_interval: Print stats every N epochs
        verbose: If True, show full output from each run
    """
    # Import here to avoid circular imports
    from integration import run_complete

    # Initialize learner ONCE - persists across all epochs
    pl_learner = PreferenceLearner(alpha=0.05, bound=1.0)

    print("=" * 70)
    print("TRAINING LOOP: CONSTRAINT-FIRST LLM")
    print("कार्य (kārya) happens before ज्ञान (jñāna)")
    print("=" * 70)
    print()
    print(f"Epochs: {epochs}")
    print(f"Print interval: every {print_interval} epochs")
    print(f"Learner: alpha={pl_learner.alpha}, bound={pl_learner.bound}")
    print()

    # Track metrics over time
    metrics_history = []

    # Training loop
    for epoch in range(epochs):
        # Run one complete iteration
        # Note: main() will use the global learner instance
        # We need to pass it or make it accessible

        # Suppress output if not verbose
        try:
            if verbose or epoch % print_interval == 0:
                result = run_single_epoch(pl_learner)
            else:
                # Redirect stdout to suppress output
                import io
                import contextlib
                f = io.StringIO()
                with contextlib.redirect_stdout(f):
                    result = run_single_epoch(pl_learner)
        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"Error at epoch {epoch}: {e}")
            continue

        # Collect stats every interval
        if epoch % print_interval == 0:
            stats = pl_learner.get_stats()
            metrics_history.append({
                'epoch': epoch,
                'stats': stats,
                'result': result if 'result' in locals() else None
            })

            print(f"\nEpoch {epoch:4d}: "
                  f"edges={stats['total_edges']:4d}, "
                  f"avg_bias={stats['avg_bias']:+.4f}, "
                  f"max_bias={stats['max_bias']:+.4f}, "
                  f"min_bias={stats['min_bias']:+.4f}")

    # Final summary
    print()
    print("=" * 70)
    print("TRAINING COMPLETE")
    print("=" * 70)
    print()

    if metrics_history:
        initial_stats = metrics_history[0]['stats']
        end_stats = metrics_history[-1]['stats']

        print("Learning Progress:")
        print(f"  Total edges: {initial_stats['total_edges']} → {end_stats['total_edges']}")
        print(f"  Avg bias: {initial_stats['avg_bias']:+.4f} → {end_stats['avg_bias']:+.4f}")
        print(f"  Max bias: {initial_stats['max_bias']:+.4f} → {end_stats['max_bias']:+.4f}")
        print(f"  Min bias: {initial_stats['min_bias']:+.4f} → {end_stats['min_bias']:+.4f}")

        # Calculate change
        bias_change = end_stats['avg_bias'] - initial_stats['avg_bias']
        max_separation = end_stats['max_bias'] - end_stats['min_bias']

        print()
        print("Key Metrics:")
        drift_label = (
            'increasing' if bias_change > 0
            else 'stable' if abs(bias_change) < 0.001
            else 'decreasing'
        )
        sep_label = 'separating' if max_separation > 0.1 else 'not separating yet'
        print(f"  Bias drift: {bias_change:+.4f} ({drift_label})")
        print(f"  Max separation: {max_separation:.4f} ({sep_label})")
        print()

        if abs(bias_change) < 0.001 and max_separation < 0.1 and epochs >= 100:
            print(f"⚠ WARNING: Little learning observed after {epochs} epochs.")
            print("  Consider:")
            print("    - Increasing learning_rate")
            print("    - Checking if transitions are being observed correctly")
            print("    - Verifying learner.observe() is called during generation")
        else:
            print("✓ Learning is progressing as expected.")

    print()
    return pl_learner, metrics_history


def run_single_epoch(learner):
    """
    Run a single epoch of the complete pipeline with persistent learner.

    Args:
        learner: PreferenceLearner instance (persists across epochs)

    Returns dict with results for analysis.
    """
    # Import here to avoid circular imports
    from integration import run_complete

    # Suppress output by redirecting stdout
    import io
    import contextlib

    # Call main() with our persistent learner
    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        try:
            run_complete.main(learner=learner)
            output = f.getvalue()
        except Exception as e:
            output = str(e)
            raise

    # Extract some results from output if needed
    # For now, just return basic dict
    result = {
        'output': output,
        'learner_stats': learner.get_stats()
    }

    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Train Constraint-First LLM")
    parser.add_argument("--epochs", type=int, default=200, help="Number of training epochs")
    parser.add_argument("--interval", type=int, default=10, help="Print stats every N epochs")
    parser.add_argument("--verbose", action="store_true", help="Show full output from each run")

    args = parser.parse_args()

    trained_learner, history = run_training(
        epochs=args.epochs,
        print_interval=args.interval,
        verbose=args.verbose
    )

    print("\nTraining complete. Final learner state:")
    final_stats = trained_learner.get_stats()
    print(f"  {final_stats}")
