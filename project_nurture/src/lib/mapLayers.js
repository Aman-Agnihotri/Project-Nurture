export const cleanupLeafletLayers = layers => {
  layers.forEach(layer => {
    layer.eachLayer?.(child => child.off?.());
    layer.off?.();
    layer.clearLayers?.();
    layer.remove?.();
  });
};
