import pandas as pd
import numpy as np
from abc import ABC, abstractmethod

class BaseTransformer(ABC):
    """
    Classe base abstrata para transformações de dados.
    """
    @abstractmethod
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aplica as transformações no DataFrame e retorna o DataFrame tratado.
        """
        pass

class AccidentsTransformer(BaseTransformer):
    """
    Transformador para os dados de acidentes da PRF.
    """
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        print("Transformando dados de acidentes...")
        df_clean = df.copy()
        
        # Normalização decimal de vírgula para ponto e conversão para float
        df_clean['latitude'] = pd.to_numeric(df_clean['latitude'].astype(str).str.replace(',', '.'), errors='coerce')
        df_clean['longitude'] = pd.to_numeric(df_clean['longitude'].astype(str).str.replace(',', '.'), errors='coerce')
        df_clean['km'] = pd.to_numeric(df_clean['km'].astype(str).str.replace(',', '.'), errors='coerce')
        
        # Padronização da chave rodovia BR para string de 3 dígitos com preenchimento (ex: '060', '153')
        df_clean['br'] = df_clean['br'].astype(str).str.replace('.0', '', regex=False).str.strip().str.zfill(3)
        
        return df_clean

class RadarsTransformer(BaseTransformer):
    """
    Transformador para os dados de radares de velocidade (PNCV).
    """
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        print("Transformando dados de radares (PNCV)...")
        df_clean = df.copy()
        df_clean.columns = [c.strip() for c in df_clean.columns]
        
        coords_col = 'Coordenadas (Lat/Long)'
        if coords_col not in df_clean.columns:
            # Fallback para caso as colunas estejam em caixa diferente
            coords_col = [c for c in df_clean.columns if 'coordenadas' in c.lower()][0]
            
        def extract_coords_from_formula(val):
            if pd.isnull(val): return None, None
            val_str = str(val).strip()
            if val_str.startswith('='):
                val_str = val_str[1:]
            parts = val_str.split('/')
            if len(parts) == 2:
                try:
                    # Substitui vírgula por ponto para suportar decimais em formato de texto brasileiro
                    lat = float(parts[0].replace(',', '.').strip())
                    lon = float(parts[1].replace(',', '.').strip())
                    return lat, lon
                except ValueError:
                    pass
            return None, None
            
        lats, lons = [], []
        for val in df_clean[coords_col]:
            lat, lon = extract_coords_from_formula(val)
            lats.append(lat)
            lons.append(lon)
            
        df_clean['latitude'] = lats
        df_clean['longitude'] = lons
        
        # Limpeza do Km e Rodovia
        df_clean['km'] = pd.to_numeric(df_clean['Km'].astype(str).str.replace(',', '.'), errors='coerce')
        df_clean['br'] = df_clean['Rodovia'].astype(str).str.replace('BR-', '', regex=False).str.strip().str.zfill(3)
        
        # Remover colunas brutas que não serão necessárias no banco
        df_clean = df_clean.drop(columns=[coords_col, 'Km', 'Rodovia'], errors='ignore')
        
        return df_clean

class SignalingTransformer(BaseTransformer):
    """
    Transformador para os dados de sinalização de ultrapassagem (JSON).
    """
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        print("Transformando dados de sinalização (placas)...")
        df_clean = df.copy()
        
        # Normalização decimal em float
        for col in ['km_m_inicio', 'latitude_inicio', 'longitude_inicio', 'km_m_final', 'latitude_final', 'longitude_final']:
            if col in df_clean.columns:
                df_clean[col] = pd.to_numeric(df_clean[col].astype(str).str.replace(',', '.'), errors='coerce')
                
        # Normalização da rodovia
        if 'rodovia' in df_clean.columns:
            df_clean['br'] = df_clean['rodovia'].astype(str).str.replace('BR-', '', regex=False).str.strip().str.zfill(3)
            df_clean = df_clean.drop(columns=['rodovia'], errors='ignore')
            
        return df_clean
