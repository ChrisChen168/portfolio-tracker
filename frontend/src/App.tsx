import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts'

type AssetType = 'stock' | 'crypto' | 'bond' | 'cash'

type Asset = {
  id: number
  name: string
  symbol: string
  type: AssetType
  amount: number
  buy_price: number
  current_price: number
}

type PortfolioItem = {
  asset: Asset
  value: number
  pnl: number
}

type Portfolio = {
  total_value: number
  items: PortfolioItem[]
}

const COLORS = ['#0ea5e9','#22c55e','#f59e0b','#ef4444','#8b5cf6','#14b8a6']

async function fetchPortfolio(): Promise<Portfolio> {
  const { data } = await axios.get('/api/portfolio')
  return data
}

async function fetchPriceFor(asset: Asset): Promise<number> {
  if (asset.type === 'stock') {
    const { data } = await axios.get(`/api/price/stock/${asset.symbol}`)
    return data.price
  }
  if (asset.type === 'crypto') {
    const { data } = await axios.get(`/api/price/crypto/${asset.symbol}`)
    return data.price
  }
  if (asset.type === 'bond') {
    const { data } = await axios.get(`/api/price/bond/${asset.symbol}`)
    return data.price
  }
  const { data } = await axios.get(`/api/price/cash/${asset.symbol}`)
  return data.price
}

export default function App() {
  const queryClient = useQueryClient()
  const { data: portfolio, isLoading } = useQuery({
    queryKey: ['portfolio'],
    queryFn: fetchPortfolio,
    refetchInterval: 30000,
  })

  const [form, setForm] = useState<{id?: number, name: string, symbol: string, type: AssetType, amount: number, buy_price: number}>({
    name: '', symbol: '', type: 'stock', amount: 0, buy_price: 0
  })

  const createOrUpdateMutation = useMutation({
    mutationFn: async () => {
      if (form.id) {
        await axios.put(`/api/assets/${form.id}`, {
          name: form.name,
          symbol: form.symbol,
          type: form.type,
          amount: form.amount,
          buy_price: form.buy_price,
        })
      } else {
        await axios.post('/api/assets/', {
          name: form.name,
          symbol: form.symbol,
          type: form.type,
          amount: form.amount,
          buy_price: form.buy_price,
        })
      }
    },
    onSuccess: () => {
      setForm({ name: '', symbol: '', type: 'stock', amount: 0, buy_price: 0 })
      queryClient.invalidateQueries({ queryKey: ['portfolio'] })
    }
  })

  const deleteMutation = useMutation({
    mutationFn: async (id: number) => {
      await axios.delete(`/api/assets/${id}`)
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['portfolio'] })
  })

  const refreshPrices = async () => {
    if (!portfolio) return
    const updates = await Promise.all(portfolio.items.map(async (it) => ({
      id: it.asset.id,
      price: await fetchPriceFor(it.asset)
    })))
    await Promise.all(updates.map(u => axios.put(`/api/assets/${u.id}`, { current_price: u.price })))
    queryClient.invalidateQueries({ queryKey: ['portfolio'] })
  }

  return (
    <div className="min-h-screen">
      <nav className="bg-white shadow-sm">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center gap-6">
          <div className="font-semibold">Portfolio Tracker</div>
          <div className="text-sm text-gray-600 flex gap-4">
            <a className="hover:text-gray-900" href="#">Dashboard</a>
            <a className="hover:text-gray-900" href="#">Add Asset</a>
            <a className="hover:text-gray-900" href="#">Settings</a>
          </div>
          <div className="ml-auto">
            <button onClick={refreshPrices} className="px-3 py-1.5 rounded-md bg-blue-600 text-white text-sm hover:bg-blue-700">Refresh Prices</button>
          </div>
        </div>
      </nav>

      <main className="max-w-6xl mx-auto p-4 space-y-6">
        <div className="grid md:grid-cols-3 gap-4">
          <div className="bg-white rounded-xl shadow p-4">
            <div className="text-sm text-gray-500">Total Portfolio Value</div>
            <div className="text-3xl font-semibold">${portfolio?.total_value.toLocaleString() ?? '0.00'}</div>
          </div>
          <div className="bg-white rounded-xl shadow p-4 md:col-span-2">
            <div className="h-56">
              {isLoading ? (
                <div className="h-full flex items-center justify-center text-gray-500">Loading...</div>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie dataKey="value" data={(portfolio?.items ?? []).map(i => ({ name: `${i.asset.symbol} (${i.asset.type})`, value: i.value }))} outerRadius={80} label>
                      {(portfolio?.items ?? []).map((_, idx) => (
                        <Cell key={idx} fill={COLORS[idx % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              )}
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow p-4">
          <div className="font-medium mb-3">Assets</div>
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead className="text-left text-gray-500">
                <tr>
                  <th className="py-2 pr-4">Symbol</th>
                  <th className="py-2 pr-4">Type</th>
                  <th className="py-2 pr-4">Amount</th>
                  <th className="py-2 pr-4">Current Price</th>
                  <th className="py-2 pr-4">Value</th>
                  <th className="py-2 pr-4">P/L</th>
                  <th className="py-2 pr-4"></th>
                </tr>
              </thead>
              <tbody>
                {(portfolio?.items ?? []).map((it) => (
                  <tr key={it.asset.id} className="border-t">
                    <td className="py-2 pr-4 font-medium">{it.asset.symbol}</td>
                    <td className="py-2 pr-4">{it.asset.type}</td>
                    <td className="py-2 pr-4">{it.asset.amount}</td>
                    <td className="py-2 pr-4">${it.asset.current_price.toFixed(2)}</td>
                    <td className="py-2 pr-4">${it.value.toFixed(2)}</td>
                    <td className={`py-2 pr-4 ${it.pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>{it.pnl.toFixed(2)}</td>
                    <td className="py-2 pr-4 flex gap-2">
                      <button onClick={() => setForm({ id: it.asset.id, name: it.asset.name, symbol: it.asset.symbol, type: it.asset.type as AssetType, amount: it.asset.amount, buy_price: it.asset.buy_price })} className="px-2 py-1 rounded bg-yellow-50 text-yellow-800 hover:bg-yellow-100">Edit</button>
                      <button onClick={() => deleteMutation.mutate(it.asset.id)} className="px-2 py-1 rounded bg-red-50 text-red-700 hover:bg-red-100">Delete</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow p-4">
          <div className="font-medium mb-3">{form.id ? 'Edit Asset' : 'Add Asset'}</div>
          <form onSubmit={(e) => { e.preventDefault(); createOrUpdateMutation.mutate(); }} className="grid md:grid-cols-6 gap-3">
            <input className="border rounded-md px-3 py-2" placeholder="Name" value={form.name} onChange={e => setForm(f => ({...f, name: e.target.value}))} />
            <input className="border rounded-md px-3 py-2" placeholder="Symbol" value={form.symbol} onChange={e => setForm(f => ({...f, symbol: e.target.value}))} />
            <select className="border rounded-md px-3 py-2" value={form.type} onChange={e => setForm(f => ({...f, type: e.target.value as AssetType}))}>
              <option value="stock">Stock</option>
              <option value="crypto">Crypto</option>
              <option value="bond">Bond</option>
              <option value="cash">Cash</option>
            </select>
            <input className="border rounded-md px-3 py-2" placeholder="Amount" type="number" step="any" value={form.amount} onChange={e => setForm(f => ({...f, amount: parseFloat(e.target.value)}))} />
            <input className="border rounded-md px-3 py-2" placeholder="Buy Price" type="number" step="any" value={form.buy_price} onChange={e => setForm(f => ({...f, buy_price: parseFloat(e.target.value)}))} />
            <div className="flex items-center gap-2">
              <button className="px-3 py-2 rounded-md bg-blue-600 text-white hover:bg-blue-700" type="submit">{form.id ? 'Save' : 'Add'}</button>
              {form.id && (
                <button type="button" onClick={() => setForm({ name: '', symbol: '', type: 'stock', amount: 0, buy_price: 0 })} className="px-3 py-2 rounded-md bg-gray-100 text-gray-800 hover:bg-gray-200">Cancel</button>
              )}
            </div>
          </form>
        </div>
      </main>
    </div>
  )
}


