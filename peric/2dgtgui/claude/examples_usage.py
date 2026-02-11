"""
CAFFA Visualization - Example Usage Script

This script demonstrates how to use the CAFFA visualization tools
for common CFD post-processing tasks.
"""

import numpy as np
import matplotlib.pyplot as plt
from caffa_reader import CAFFAReader, create_sample_data


def example_1_basic_contour():
    """Example 1: Basic contour plot"""
    print("Example 1: Basic Contour Plot")
    print("-" * 50)
    
    # Create sample data
    reader = CAFFAReader()
    reader.data = create_sample_data(50, 30)
    
    # Get coordinates and velocity magnitude
    x, y = reader.get_coordinates()
    vmag = reader.get_cell_centered_data('vmag')
    
    # Create plot
    plt.figure(figsize=(10, 6))
    contour = plt.contourf(x, y, vmag, levels=20, cmap='jet')
    plt.colorbar(contour, label='Velocity Magnitude')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Velocity Magnitude - Driven Cavity')
    plt.axis('equal')
    plt.tight_layout()
    plt.savefig('/mnt/user-data/outputs/example1_contour.png', dpi=150)
    print("Saved: example1_contour.png")
    plt.close()


def example_2_vector_field():
    """Example 2: Vector field with contours"""
    print("\nExample 2: Vector Field")
    print("-" * 50)
    
    reader = CAFFAReader()
    reader.data = create_sample_data(40, 30)
    
    x, y = reader.get_coordinates()
    u = reader.get_cell_centered_data('u')
    v = reader.get_cell_centered_data('v')
    vmag = reader.get_cell_centered_data('vmag')
    
    # Create plot
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Contours
    contour = ax.contourf(x, y, vmag, levels=15, cmap='viridis', alpha=0.7)
    plt.colorbar(contour, ax=ax, label='Velocity Magnitude')
    
    # Vectors (subsampled)
    step = 4
    ax.quiver(x[::step, ::step], y[::step, ::step],
              u[::step, ::step], v[::step, ::step],
              scale=15, color='white', width=0.003, alpha=0.8)
    
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_title('Velocity Field with Vectors')
    ax.set_aspect('equal')
    plt.tight_layout()
    plt.savefig('/mnt/user-data/outputs/example2_vectors.png', dpi=150)
    print("Saved: example2_vectors.png")
    plt.close()


def example_3_streamlines():
    """Example 3: Streamline visualization"""
    print("\nExample 3: Streamlines")
    print("-" * 50)
    
    reader = CAFFAReader()
    reader.data = create_sample_data(60, 40)
    
    x, y = reader.get_coordinates()
    u = reader.get_cell_centered_data('u')
    v = reader.get_cell_centered_data('v')
    p = reader.get_cell_centered_data('p')
    
    # Create plot
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Pressure contours
    contour = ax.contourf(x, y, p, levels=20, cmap='coolwarm', alpha=0.6)
    plt.colorbar(contour, ax=ax, label='Pressure')
    
    # Streamlines
    ax.streamplot(x, y, u, v, density=2, color='black',
                  linewidth=1.5, arrowsize=1.5)
    
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_title('Streamlines with Pressure Contours')
    ax.set_aspect('equal')
    plt.tight_layout()
    plt.savefig('/mnt/user-data/outputs/example3_streamlines.png', dpi=150)
    print("Saved: example3_streamlines.png")
    plt.close()


def example_4_multi_field():
    """Example 4: Multi-field comparison"""
    print("\nExample 4: Multi-Field Comparison")
    print("-" * 50)
    
    reader = CAFFAReader()
    reader.data = create_sample_data(40, 30)
    
    x, y = reader.get_coordinates()
    
    # Create subplot figure
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('CAFFA CFD Results - Multi-Field View', fontsize=16)
    
    # Velocity magnitude
    vmag = reader.get_cell_centered_data('vmag')
    c1 = axes[0, 0].contourf(x, y, vmag, levels=20, cmap='jet')
    axes[0, 0].set_title('Velocity Magnitude')
    axes[0, 0].set_xlabel('X')
    axes[0, 0].set_ylabel('Y')
    axes[0, 0].set_aspect('equal')
    plt.colorbar(c1, ax=axes[0, 0])
    
    # Pressure
    p = reader.get_cell_centered_data('p')
    c2 = axes[0, 1].contourf(x, y, p, levels=20, cmap='coolwarm')
    axes[0, 1].set_title('Pressure')
    axes[0, 1].set_xlabel('X')
    axes[0, 1].set_ylabel('Y')
    axes[0, 1].set_aspect('equal')
    plt.colorbar(c2, ax=axes[0, 1])
    
    # Temperature
    t = reader.get_cell_centered_data('t')
    c3 = axes[1, 0].contourf(x, y, t, levels=20, cmap='hot')
    axes[1, 0].set_title('Temperature')
    axes[1, 0].set_xlabel('X')
    axes[1, 0].set_ylabel('Y')
    axes[1, 0].set_aspect('equal')
    plt.colorbar(c3, ax=axes[1, 0])
    
    # Turbulent kinetic energy
    te = reader.get_cell_centered_data('te')
    c4 = axes[1, 1].contourf(x, y, te, levels=20, cmap='plasma')
    axes[1, 1].set_title('Turbulent Kinetic Energy')
    axes[1, 1].set_xlabel('X')
    axes[1, 1].set_ylabel('Y')
    axes[1, 1].set_aspect('equal')
    plt.colorbar(c4, ax=axes[1, 1])
    
    plt.tight_layout()
    plt.savefig('/mnt/user-data/outputs/example4_multifield.png', dpi=150)
    print("Saved: example4_multifield.png")
    plt.close()


def example_5_statistics():
    """Example 5: Field statistics and analysis"""
    print("\nExample 5: Field Statistics")
    print("-" * 50)
    
    reader = CAFFAReader()
    reader.data = create_sample_data(50, 40)
    
    # Calculate statistics for all fields
    fields = {
        'Velocity Magnitude': 'vmag',
        'U Velocity': 'u',
        'V Velocity': 'v',
        'Pressure': 'p',
        'Temperature': 't',
        'TKE': 'te'
    }
    
    print("\nField Statistics:")
    print("=" * 70)
    print(f"{'Field':<20} {'Min':>12} {'Max':>12} {'Mean':>12} {'Std Dev':>12}")
    print("-" * 70)
    
    stats_data = []
    for name, field_key in fields.items():
        data = reader.get_cell_centered_data(field_key)
        stats = {
            'name': name,
            'min': np.min(data),
            'max': np.max(data),
            'mean': np.mean(data),
            'std': np.std(data)
        }
        stats_data.append(stats)
        print(f"{name:<20} {stats['min']:>12.6f} {stats['max']:>12.6f} "
              f"{stats['mean']:>12.6f} {stats['std']:>12.6f}")
    
    print("=" * 70)
    
    # Create statistics visualization
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))
    
    # Min/Max comparison
    field_names = [s['name'] for s in stats_data]
    mins = [s['min'] for s in stats_data]
    maxs = [s['max'] for s in stats_data]
    
    x_pos = np.arange(len(field_names))
    width = 0.35
    
    axes[0].bar(x_pos - width/2, mins, width, label='Min', alpha=0.8)
    axes[0].bar(x_pos + width/2, maxs, width, label='Max', alpha=0.8)
    axes[0].set_xticks(x_pos)
    axes[0].set_xticklabels(field_names, rotation=45, ha='right')
    axes[0].set_ylabel('Value')
    axes[0].set_title('Field Min/Max Comparison')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Mean and std dev
    means = [s['mean'] for s in stats_data]
    stds = [s['std'] for s in stats_data]
    
    axes[1].errorbar(x_pos, means, yerr=stds, fmt='o-', capsize=5,
                     linewidth=2, markersize=8)
    axes[1].set_xticks(x_pos)
    axes[1].set_xticklabels(field_names, rotation=45, ha='right')
    axes[1].set_ylabel('Value')
    axes[1].set_title('Field Mean ± Std Dev')
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/mnt/user-data/outputs/example5_statistics.png', dpi=150)
    print("\nSaved: example5_statistics.png")
    plt.close()


def example_6_custom_analysis():
    """Example 6: Custom derived quantities"""
    print("\nExample 6: Custom Analysis")
    print("-" * 50)
    
    reader = CAFFAReader()
    reader.data = create_sample_data(50, 40)
    
    x, y = reader.get_coordinates()
    u = reader.get_cell_centered_data('u')
    v = reader.get_cell_centered_data('v')
    p = reader.get_cell_centered_data('p')
    
    # Calculate derived quantities
    vmag = np.sqrt(u**2 + v**2)
    kinetic_energy = 0.5 * (u**2 + v**2)
    
    # Simple vorticity estimate (using finite differences)
    dvdx = np.gradient(v, axis=1)
    dudy = np.gradient(u, axis=0)
    vorticity = dvdx - dudy
    
    # Create visualization
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    
    # Velocity magnitude
    c1 = axes[0].contourf(x, y, vmag, levels=20, cmap='jet')
    axes[0].set_title('Velocity Magnitude')
    axes[0].set_aspect('equal')
    plt.colorbar(c1, ax=axes[0])
    
    # Kinetic energy
    c2 = axes[1].contourf(x, y, kinetic_energy, levels=20, cmap='hot')
    axes[1].set_title('Kinetic Energy')
    axes[1].set_aspect('equal')
    plt.colorbar(c2, ax=axes[1])
    
    # Vorticity
    c3 = axes[2].contourf(x, y, vorticity, levels=20, cmap='RdBu_r')
    axes[2].set_title('Vorticity')
    axes[2].set_aspect('equal')
    plt.colorbar(c3, ax=axes[2])
    
    for ax in axes:
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
    
    plt.tight_layout()
    plt.savefig('/mnt/user-data/outputs/example6_custom.png', dpi=150)
    print("Saved: example6_custom.png")
    plt.close()
    
    # Print statistics
    print(f"\nKinetic Energy: min={np.min(kinetic_energy):.6f}, "
          f"max={np.max(kinetic_energy):.6f}")
    print(f"Vorticity: min={np.min(vorticity):.6f}, "
          f"max={np.max(vorticity):.6f}")


def main():
    """Run all examples"""
    print("=" * 60)
    print("CAFFA Visualization - Example Usage")
    print("=" * 60)
    
    # Run examples
    example_1_basic_contour()
    example_2_vector_field()
    example_3_streamlines()
    example_4_multi_field()
    example_5_statistics()
    example_6_custom_analysis()
    
    print("\n" + "=" * 60)
    print("All examples completed successfully!")
    print("Output images saved to /mnt/user-data/outputs/")
    print("=" * 60)


if __name__ == '__main__':
    main()
