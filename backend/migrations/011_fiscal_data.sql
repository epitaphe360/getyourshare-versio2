-- Données initiales: Taux de TVA (à exécuter APRÈS 010_fiscal_minimal.sql)

INSERT INTO vat_rates (country, rate, category, description, valid_from) 
VALUES 
('MA', 20.00, 'standard', 'TVA normale Maroc', '2024-01-01'),
('MA', 14.00, 'intermediate', 'TVA intermédiaire Maroc', '2024-01-01'),
('MA', 10.00, 'reduced', 'TVA réduite Maroc', '2024-01-01'),
('MA', 7.00, 'super_reduced', 'TVA super réduite Maroc', '2024-01-01'),
('MA', 0.00, 'zero', 'Exonération TVA Maroc', '2024-01-01'),
('FR', 20.00, 'standard', 'TVA normale France', '2024-01-01'),
('FR', 10.00, 'intermediate', 'TVA intermédiaire France', '2024-01-01'),
('FR', 5.50, 'reduced', 'TVA réduite France', '2024-01-01'),
('FR', 2.10, 'super_reduced', 'TVA super réduite France', '2024-01-01'),
('FR', 0.00, 'zero', 'Franchise TVA France', '2024-01-01'),
('US', 7.25, 'california', 'Sales Tax California', '2024-01-01'),
('US', 6.00, 'texas', 'Sales Tax Texas', '2024-01-01'),
('US', 6.25, 'illinois', 'Sales Tax Illinois', '2024-01-01'),
('US', 6.00, 'florida', 'Sales Tax Florida', '2024-01-01'),
('US', 0.00, 'zero', 'No Sales Tax', '2024-01-01')
ON CONFLICT DO NOTHING;
