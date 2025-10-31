//! DNA Extraction Benchmarks
//!
//! Run with: cargo bench

use criterion::{black_box, criterion_group, criterion_main, BenchmarkId, Criterion};
use image::{ImageBuffer, Rgb};
use protrace_dna::{compute_dhash, compute_grid_hash, DnaExtractor};

fn create_test_image(width: u32, height: u32) -> ImageBuffer<Rgb<u8>, Vec<u8>> {
    ImageBuffer::from_fn(width, height, |x, y| {
        let r = ((x + y) % 256) as u8;
        let g = ((x * 2 + y) % 256) as u8;
        let b = ((x + y * 2) % 256) as u8;
        Rgb([r, g, b])
    })
}

fn bench_dhash(c: &mut Criterion) {
    let mut group = c.benchmark_group("dhash");

    for size in [512, 1024, 2048] {
        let img = create_test_image(size, size);
        group.bench_with_input(BenchmarkId::from_parameter(size), &img, |b, img| {
            b.iter(|| {
                let _ = compute_dhash(black_box(img), 8);
            });
        });
    }

    group.finish();
}

fn bench_grid_hash(c: &mut Criterion) {
    let mut group = c.benchmark_group("grid_hash");

    for size in [512, 1024, 2048] {
        let img = create_test_image(size, size);
        group.bench_with_input(BenchmarkId::from_parameter(size), &img, |b, img| {
            b.iter(|| {
                let _ = compute_grid_hash(black_box(img));
            });
        });
    }

    group.finish();
}

fn bench_full_dna(c: &mut Criterion) {
    let mut group = c.benchmark_group("full_dna");

    let extractor = DnaExtractor::new();

    for size in [512, 1024, 2048, 4096] {
        let img = image::DynamicImage::ImageRgb8(create_test_image(size, size));
        group.bench_with_input(BenchmarkId::from_parameter(size), &img, |b, img| {
            b.iter(|| {
                let _ = extractor.extract(black_box(img));
            });
        });
    }

    group.finish();
}

fn bench_hamming_distance(c: &mut Criterion) {
    use protrace_dna::utils::hamming_distance;

    let hash1 = "cb23db940ce3747e036e3e910c60d69a5965cddebe0afbfe0455535edabaf822";
    let hash2 = "cb23db940ce3747e036e3e910c60d69a5965cddebe0afbfe0455535edabaf823";

    c.bench_function("hamming_distance", |b| {
        b.iter(|| hamming_distance(black_box(hash1), black_box(hash2)));
    });
}

fn bench_similarity(c: &mut Criterion) {
    use protrace_dna::utils::similarity;

    let hash1 = "cb23db940ce3747e036e3e910c60d69a5965cddebe0afbfe0455535edabaf822";
    let hash2 = "cb23db940ce3747e036e3e910c60d69a5965cddebe0afbfe0455535edabaf823";

    c.bench_function("similarity", |b| {
        b.iter(|| similarity(black_box(hash1), black_box(hash2)));
    });
}

criterion_group!(
    benches,
    bench_dhash,
    bench_grid_hash,
    bench_full_dna,
    bench_hamming_distance,
    bench_similarity
);
criterion_main!(benches);
