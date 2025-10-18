"""
Nutrition5k Dataset Setup and Label Generation Script

This script:
1. Downloads Nutrition5k dataset from Google Cloud Storage
2. Extracts and organizes the data
3. Generates multi-label food pyramid classifications
4. Creates train/val split

Requirements:
- gsutil (Google Cloud Storage tool)
- Python 3.7+
- pandas, numpy
"""

import os
import subprocess
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from collections import defaultdict

class Nutrition5kSetup:
    def __init__(self, base_dir="./nutrition5k_data"):
        """
        Initialize setup with base directory for storing dataset.
        
        Args:
            base_dir: Directory where dataset will be downloaded and organized
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Dataset paths
        self.images_dir = self.base_dir / "images"
        self.metadata_dir = self.base_dir / "metadata"
        self.labels_dir = self.base_dir / "labels"
        
        # GCS bucket URL
        self.gcs_bucket = "gs://nutrition5k_dataset/nutrition5k_dataset"
        
    def check_gsutil(self):
        """Check if gsutil is installed."""
        try:
            subprocess.run(["gsutil", "--version"], 
                         capture_output=True, check=True)
            print("✓ gsutil is installed")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("✗ gsutil is NOT installed")
            print("\nTo install gsutil:")
            print("1. Install Google Cloud SDK:")
            print("   https://cloud.google.com/sdk/docs/install")
            print("2. Or use pip: pip install gsutil")
            return False
    
    def download_metadata(self):
        """Download only metadata files (small, ~few MB)."""
        print("\n" + "="*60)
        print("STEP 1: Downloading Metadata Files")
        print("="*60)
        
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
        
        metadata_files = [
            "dish_metadata_cafe1.csv",
            "dish_metadata_cafe2.csv",
            "ingredients_metadata.csv"
        ]
        
        for filename in metadata_files:
            gcs_path = f"{self.gcs_bucket}/metadata/{filename}"
            local_path = self.metadata_dir / filename
            
            if local_path.exists():
                print(f"✓ {filename} already exists, skipping...")
                continue
            
            print(f"Downloading {filename}...")
            try:
                subprocess.run(
                    ["gsutil", "cp", gcs_path, str(local_path)],
                    check=True
                )
                print(f"✓ {filename} downloaded")
            except subprocess.CalledProcessError as e:
                print(f"✗ Failed to download {filename}: {e}")
                return False
        
        print("\n✓ All metadata files downloaded successfully!")
        return True
    
    def download_images_sample(self, num_samples=100):
        """
        Download a SAMPLE of images for testing (instead of all 5000).
        Full dataset is ~180GB, so we start with a small sample.
        
        Args:
            num_samples: Number of dish images to download
        """
        print("\n" + "="*60)
        print(f"STEP 2: Downloading Sample Images ({num_samples} dishes)")
        print("="*60)
        print("Note: Full dataset is ~180GB. Starting with sample for testing.")
        
        self.images_dir.mkdir(parents=True, exist_ok=True)
        
        # Read metadata to get dish IDs (with error handling for inconsistent columns)
        cafe1_df = pd.read_csv(self.metadata_dir / "dish_metadata_cafe1.csv", 
                               on_bad_lines='skip', engine='python')
        cafe2_df = pd.read_csv(self.metadata_dir / "dish_metadata_cafe2.csv",
                               on_bad_lines='skip', engine='python')
        
        # Debug: print columns to see what's available
        print(f"Available columns: {cafe1_df.columns.tolist()[:10]}...")
        
        # Find the dish ID column (might be 'dish_id' or first column)
        dish_id_col = 'dish_id' if 'dish_id' in cafe1_df.columns else cafe1_df.columns[0]
        
        # Get sample dish IDs
        all_dish_ids = list(cafe1_df[dish_id_col].values) + list(cafe2_df[dish_id_col].values)
        sample_dish_ids = all_dish_ids[:num_samples]
        
        print(f"Selected {len(sample_dish_ids)} dishes to download...")
        
        downloaded = 0
        for i, dish_id in enumerate(sample_dish_ids):
            # We'll download overhead RGB images (simplest, single image per dish)
            gcs_path = f"{self.gcs_bucket}/imagery/realsense_overhead/{dish_id}/rgb.png"
            
            dish_dir = self.images_dir / str(dish_id)
            dish_dir.mkdir(parents=True, exist_ok=True)
            local_path = dish_dir / "rgb.png"
            
            if local_path.exists():
                downloaded += 1
                continue
            
            try:
                subprocess.run(
                    ["gsutil", "-q", "cp", gcs_path, str(local_path)],
                    check=True,
                    stderr=subprocess.DEVNULL
                )
                downloaded += 1
                if (i + 1) % 10 == 0:
                    print(f"Downloaded {i + 1}/{len(sample_dish_ids)} images...")
            except subprocess.CalledProcessError:
                # Image might not exist for this dish, skip
                continue
        
        print(f"\n✓ Downloaded {downloaded} images successfully!")
        return True
    
    def download_all_images(self):
        """
        Download ALL images (WARNING: ~180GB, takes hours).
        Only use this after testing with samples!
        """
        print("\n" + "="*60)
        print("STEP 2: Downloading ALL Images (~180GB)")
        print("="*60)
        print("WARNING: This will download ~180GB of data!")
        
        response = input("Are you sure you want to continue? (yes/no): ")
        if response.lower() != 'yes':
            print("Download cancelled.")
            return False
        
        self.images_dir.mkdir(parents=True, exist_ok=True)
        
        # Download all overhead RGB images
        gcs_path = f"{self.gcs_bucket}/imagery/realsense_overhead/"
        
        print("Starting download... This may take several hours.")
        try:
            subprocess.run(
                ["gsutil", "-m", "cp", "-r", gcs_path, str(self.images_dir)],
                check=True
            )
            print("\n✓ All images downloaded successfully!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Download failed: {e}")
            return False
    
    def generate_labels(self, 
                       protein_threshold=10,
                       fat_threshold=5, 
                       carb_threshold=15):
        """
        Generate multi-label food pyramid classifications.
        
        Args:
            protein_threshold: Grams of protein for protein category
            fat_threshold: Grams of fat for fats category
            carb_threshold: Grams of carbs for carbs category
        """
        print("\n" + "="*60)
        print("STEP 3: Generating Food Pyramid Labels")
        print("="*60)
        
        self.labels_dir.mkdir(parents=True, exist_ok=True)
        
        # Keywords for classification
        dairy_keywords = ['milk', 'cheese', 'yogurt', 'cream', 'butter', 
                         'cheddar', 'mozzarella', 'parmesan', 'dairy']
        fruit_veg_keywords = ['apple', 'banana', 'orange', 'berry', 'grape',
                             'tomato', 'lettuce', 'spinach', 'broccoli', 
                             'carrot', 'pepper', 'onion', 'cucumber',
                             'fruit', 'vegetable', 'salad', 'greens']
        
        # Process both cafes
        all_labels = []
        
        for cafe_num in [1, 2]:
            metadata_file = self.metadata_dir / f"dish_metadata_cafe{cafe_num}.csv"
            df = pd.read_csv(metadata_file, on_bad_lines='skip', engine='python')
            
            # Find dish_id column
            dish_id_col = 'dish_id' if 'dish_id' in df.columns else df.columns[0]
            
            print(f"\nProcessing Cafe {cafe_num} ({len(df)} dishes)...")
            
            for idx, row in df.iterrows():
                dish_id = row[dish_id_col]
                
                # Initialize labels [fats, protein, dairy, fruits_veg, carbs]
                labels = np.zeros(5, dtype=int)
                
                # Category 0: Fats, oils & confectionery
                if row['total_fat'] >= fat_threshold:
                    labels[0] = 1
                
                # Category 1: Meat, fish & alternatives (protein)
                if row['total_protein'] >= protein_threshold:
                    labels[1] = 1
                
                # Category 2: Milk, cheese & dairy
                ingredient_cols = [col for col in df.columns 
                                 if 'ingr_' in col and '_name' in col]
                for col in ingredient_cols:
                    if pd.notna(row[col]):
                        ingredient = str(row[col]).lower()
                        if any(kw in ingredient for kw in dairy_keywords):
                            labels[2] = 1
                            break
                
                # Category 3: Fruit & vegetables
                for col in ingredient_cols:
                    if pd.notna(row[col]):
                        ingredient = str(row[col]).lower()
                        if any(kw in ingredient for kw in fruit_veg_keywords):
                            labels[3] = 1
                            break
                
                # Category 4: Bread, cereals & potatoes (carbs)
                if row['total_carb'] >= carb_threshold:
                    labels[4] = 1
                
                all_labels.append({
                    'dish_id': dish_id,
                    'cafe': cafe_num,
                    'fats_oils': labels[0],
                    'protein': labels[1],
                    'dairy': labels[2],
                    'fruits_veg': labels[3],
                    'carbs': labels[4]
                })
        
        # Create DataFrame
        labels_df = pd.DataFrame(all_labels)
        
        # Save labels
        output_file = self.labels_dir / "food_pyramid_labels.csv"
        labels_df.to_csv(output_file, index=False)
        
        print(f"\n✓ Labels saved to {output_file}")
        
        # Print statistics
        self._print_label_statistics(labels_df)
        
        return labels_df
    
    def _print_label_statistics(self, labels_df):
        """Print distribution of labels."""
        print("\n" + "="*60)
        print("LABEL STATISTICS")
        print("="*60)
        
        categories = ['fats_oils', 'protein', 'dairy', 'fruits_veg', 'carbs']
        
        total = len(labels_df)
        for cat in categories:
            count = labels_df[cat].sum()
            pct = (count / total) * 100
            print(f"{cat:15s}: {count:4d} / {total} ({pct:5.1f}%)")
        
        # Multi-label stats
        labels_per_dish = labels_df[categories].sum(axis=1)
        print(f"\nAverage labels per dish: {labels_per_dish.mean():.2f}")
        print(f"Max labels per dish: {labels_per_dish.max()}")
        print(f"Dishes with 0 labels: {(labels_per_dish == 0).sum()}")
    
    def create_train_val_split(self, val_ratio=0.2, random_seed=42):
        """
        Create train/validation split.
        
        Args:
            val_ratio: Fraction of data for validation (default 0.2 = 20%)
            random_seed: Random seed for reproducibility
        """
        print("\n" + "="*60)
        print("STEP 4: Creating Train/Validation Split")
        print("="*60)
        
        labels_file = self.labels_dir / "food_pyramid_labels.csv"
        labels_df = pd.read_csv(labels_file, on_bad_lines='skip', engine='python')
        
        # Shuffle
        labels_df = labels_df.sample(frac=1, random_state=random_seed).reset_index(drop=True)
        
        # Split
        val_size = int(len(labels_df) * val_ratio)
        train_size = len(labels_df) - val_size
        
        train_df = labels_df.iloc[:train_size]
        val_df = labels_df.iloc[train_size:]
        
        # Save splits
        train_df.to_csv(self.labels_dir / "train_labels.csv", index=False)
        val_df.to_csv(self.labels_dir / "val_labels.csv", index=False)
        
        print(f"✓ Train set: {len(train_df)} dishes")
        print(f"✓ Validation set: {len(val_df)} dishes")
        print(f"\nFiles saved:")
        print(f"  - {self.labels_dir / 'train_labels.csv'}")
        print(f"  - {self.labels_dir / 'val_labels.csv'}")
        
        return train_df, val_df
    
    def run_full_setup(self, sample_images=True, num_samples=100):
        """
        Run complete setup process.
        
        Args:
            sample_images: If True, download sample; if False, download all
            num_samples: Number of images for sample (if sample_images=True)
        """
        print("\n" + "="*60)
        print("NUTRITION5K DATASET SETUP")
        print("="*60)
        
        # Check prerequisites
        if not self.check_gsutil():
            return False
        
        # Download metadata
        if not self.download_metadata():
            return False
        
        # Download images
        if sample_images:
            if not self.download_images_sample(num_samples):
                return False
        else:
            if not self.download_all_images():
                return False
        
        # Generate labels
        self.generate_labels()
        
        # Create train/val split
        self.create_train_val_split()
        
        print("\n" + "="*60)
        print("✓ SETUP COMPLETE!")
        print("="*60)
        print(f"\nDataset location: {self.base_dir}")
        print(f"  - Images: {self.images_dir}")
        print(f"  - Metadata: {self.metadata_dir}")
        print(f"  - Labels: {self.labels_dir}")
        print("\nNext step: Build PyTorch DataLoader")
        
        return True


# Run setup
if __name__ == "__main__":
    setup = Nutrition5kSetup(base_dir="./nutrition5k_data")
    
    # Start with sample for testing (100 images)
    # Change to sample_images=False to download all ~180GB
    setup.run_full_setup(sample_images=True, num_samples=100)