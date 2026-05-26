import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import BaseChart from './BaseChart.vue'

describe('BaseChart', () => {
  it('renderiza o stub do apexcharts com type e series', () => {
    const wrapper = mount(BaseChart, {
      props: {
        type: 'donut',
        series: [1, 2, 3],
        labels: ['A', 'B', 'C'],
      },
    })

    const stub = wrapper.find('[data-test="apexchart-stub"]')
    expect(stub.exists()).toBe(true)

    const apex = wrapper.findComponent({ name: 'ApexchartStub' })
    expect(apex.props('type')).toBe('donut')
    expect(apex.props('series')).toEqual([1, 2, 3])
    expect((apex.props('options') as { labels: string[] }).labels).toEqual([
      'A',
      'B',
      'C',
    ])
  })

  it('configura plotOptions de bar horizontal por padrão', () => {
    const wrapper = mount(BaseChart, {
      props: {
        type: 'bar',
        series: [{ name: 'casos', data: [3, 1] }],
        labels: ['Ganhou', 'Perdeu'],
      },
    })

    const apex = wrapper.findComponent({ name: 'ApexchartStub' })
    const options = apex.props('options') as {
      plotOptions: { bar: { horizontal: boolean } }
    }
    expect(options.plotOptions.bar.horizontal).toBe(true)
  })

  it('exibe centerValue customizado em radialBar', () => {
    const wrapper = mount(BaseChart, {
      props: {
        type: 'radialBar',
        series: [50],
        centerValue: 'R$ 1.000,00',
        centerLabel: 'Valor médio',
      },
    })

    const apex = wrapper.findComponent({ name: 'ApexchartStub' })
    const options = apex.props('options') as { labels: string[] }
    expect(options.labels).toEqual(['Valor médio'])
  })
})
