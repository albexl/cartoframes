
export function format(value) {
  if (Array.isArray(value)) {
    const [first, second] = value;
    if (first === -Infinity) {
      return `< ${formatValue(second)}`;
    }
    if (second === Infinity) {
      return `> ${formatValue(first)}`;
    }
    return `${formatValue(first)} - ${formatValue(second)}`;
  }
  return formatValue(value);
}

export function formatValue(value) {
  if (typeof value === 'number') {
    return formatNumber(value);
  }
  return value;
}

export function formatNumber(value) {
  const log = Math.log10(Math.abs(value));

  if ((log > 4 || log < -2.00000001) && value) {
    return value.toExponential(2);
  }
  
  if (!Number.isInteger(value)) {
    return value.toLocaleString(undefined, {
      minimumFractionDigits: 2,
      maximumFractionDigits: 3
    });
  }
  
  return value.toLocaleString();
}